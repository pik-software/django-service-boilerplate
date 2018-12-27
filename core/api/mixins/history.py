import binascii
from base64 import b64decode
from datetime import timedelta
from urllib.parse import parse_qs
from collections import OrderedDict

from django.conf import settings
from django.db.models import DateTimeField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework_filters import filterset, IsoDateTimeFilter, BooleanFilter
from django_filters.fields import IsoDateTimeField
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import (
    NotFound, ValidationError as DRFValidationError)

from core.api.pagination import StandardizedCursorPagination
from core.api.serializers import StandardizedModelSerializer


class HistoryQueryParamsValidator:

    HISTORY_DATE_PARAMS = ('gt', 'lt')
    ONLY_LAST_VERSION_ERROR_MSG = _(
        'Вы можете использовать only_last_version параметр, '
        'только с history_date, указывающий временной промежуток не больше чем'
        f' {settings.ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE} сутки')

    def __init__(
            self, query_params, lookup_url_kwarg,
            lookup_field, paginator_ordering_field):
        self.query_params = query_params.copy()
        self.lookup_url_kwarg = lookup_url_kwarg
        self.lookup_field = lookup_field
        self.paginator_ordering_field = paginator_ordering_field
        if lookup_url_kwarg in self.query_params:
            self.query_params[lookup_field] = query_params[lookup_url_kwarg]
            del self.query_params[self.lookup_url_kwarg]

    def _validate_history_date(self):
        params = {'lt': timedelta.max, 'gt': timedelta.max}
        for param_name in self.HISTORY_DATE_PARAMS:
            param_name = 'history_date__' + param_name
            param_value = self.query_params.get(param_name)
            if param_value is None:
                param_value = self.query_params.get(param_name + 'e')
            if param_value:
                try:
                    validator = IsoDateTimeField()
                    param_value = validator.strptime(
                        param_value, validator.ISO_8601)
                except ValueError:
                    pass
                else:
                    params[param_name.rsplit('_', 1)[1]] = param_value

        allowed_timedelta = timedelta(
            days=settings.ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE)
        if abs(params['lt'] - params['gt']) > allowed_timedelta:
            raise DRFValidationError(self.ONLY_LAST_VERSION_ERROR_MSG)

    def _validate_cursor(self):
        try:
            cursor = b64decode(self.query_params.get('cursor').encode('ascii'))
            cursor_param = parse_qs(cursor.decode('ascii')).get('p')
            if cursor_param:
                self.paginator_ordering_field.to_python(cursor_param[0])
        except (ValidationError, IndexError, binascii.Error):
            raise NotFound(StandardizedCursorPagination.invalid_cursor_message)

    def validate_query_params(self):
        if 'only_last_version' in self.query_params:
            if len([n for n in self.query_params if 'history_date' in n]) != 2:
                raise DRFValidationError(self.ONLY_LAST_VERSION_ERROR_MSG)
            self._validate_history_date()
        if 'cursor' in self.query_params:
            self._validate_cursor()
        return self.query_params


class HistoryPermission(BasePermission):

    def has_permission(self, request, view):
        allow_history = getattr(view, 'allow_history', False)
        if allow_history:
            opts = view.get_queryset().model._meta # noqa: pylint=protected-access
            perm_name = f'{opts.app_label}.view_historical{opts.model_name}'
            return request.user.has_perm(perm_name)
        return False


def simplify_nested_serializer(serializer):
    if isinstance(serializer, StandardizedModelSerializer):
        for _name, _field in list(serializer.fields.items()):
            if _name not in ('_uid', '_type'):
                serializer.fields.pop(_name)


class HistoryViewSetMixin:

    allow_history = False

    def get_history_serializer(self, *args, **kwargs):
        class HistorySerializer(self.get_serializer_class()):
            def to_representation(self, instance):
                ret = OrderedDict()
                fields = self._readable_fields  # noqa

                history_field_names = (
                    'history_id', 'history_date', 'history_change_reason',
                    'history_user_id', 'history_type')
                for field_name in history_field_names:
                    try:
                        value = getattr(instance, field_name)
                        ret[field_name] = value
                    except Exception:  # noqa: pylint=broad-except
                        continue

                for field in fields:
                    simplify_nested_serializer(field)
                    try:
                        attribute = field.get_attribute(instance)
                        if attribute is not None:
                            ret[field.field_name] = field.to_representation(
                                attribute)
                        else:
                            ret[field.field_name] = None
                    except AttributeError:
                        ret[field.field_name] = None

                return ret

        kwargs['context'] = self.get_serializer_context()
        return HistorySerializer(*args, **kwargs)

    def get_filtered_queryset_and_paginator(self, queryset): # noqa: pylint=invalid-name
        only_last_version_ordering = ('-uid', '-updated')

        class HistoryFilterSet(filterset.FilterSet):
            only_last_version = BooleanFilter(
                method='filter_only_last_version')

            @staticmethod
            def filter_only_last_version(queryset, name, value):
                if not value:
                    return queryset

                distinct_param = only_last_version_ordering[0].lstrip('-')
                return queryset.order_by(
                    *only_last_version_ordering).distinct(distinct_param)

            class Meta:
                model = queryset.model
                fields = {
                    'history_id': ('exact', 'gt', 'gte', 'lt', 'lte', 'in'),
                    'history_type': ('exact', 'in'),
                    'history_user_id': ('exact', 'in', 'isnull'),
                    'history_date': ('exact', 'gt', 'gte', 'lt', 'lte', 'in'),
                    self.lookup_field: (
                        'exact', 'gt', 'gte', 'lt', 'lte', 'in', 'isnull')}
                filter_overrides = {
                    DateTimeField: {'filter_class': IsoDateTimeFilter}}

        paginator = StandardizedCursorPagination()
        if 'only_last_version' in self.request.query_params:
            paginator.ordering = only_last_version_ordering

        if isinstance(paginator.ordering, (list, tuple)):
            order_field = paginator.ordering[0].strip('-')
        else:
            order_field = paginator.ordering.strip('-')
        paginator_ordering_field = queryset.model._meta.get_field(order_field) # noqa: pylint=protected-access
        query_params_validator = HistoryQueryParamsValidator(
            self.request.query_params, self.lookup_url_kwarg,
            self.lookup_field, paginator_ordering_field)
        query_params = query_params_validator.validate_query_params()

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        filter_ = HistoryFilterSet(
            query_params, queryset, request=self.request)
        return filter_.qs, paginator

    @action(detail=False, permission_classes=[HistoryPermission])
    def history(self, request, **kwargs):
        q_set = self.get_queryset().model.history.all()
        q_set, paginator = self.get_filtered_queryset_and_paginator(q_set)

        page = paginator.paginate_queryset(q_set, request)
        if page is not None:
            serializer = self.get_history_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_history_serializer(q_set, many=True)
        return Response(serializer.data)
