from collections import OrderedDict

from django_filters import filterset
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response


class BulkCreateModelMixin(CreateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializers ``many=True``.

    Example:

        class ContactViewSet(StandartizedModelViewSet):
            ...
            allow_bulk_create = True
            ...
    """
    allow_bulk_create = False

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)

        if not bulk:
            return super().create(request, *args, **kwargs)

        if not self.allow_bulk_create:
            self.permission_denied(
                request,
                message='You do not have permission to create multiple objects'
            )

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)


class HistoryViewSetMixin:
    allow_history = False

    def get_history_serializer(self, *args, **kwargs):
        class HistorySerializer(self.get_serializer_class()):
            def to_representation(self, instance):
                """
                Object instance -> Dict of primitive datatypes.
                """
                ret = OrderedDict()
                fields = self._readable_fields  # noqa

                history_field_names = [
                    'history_id', 'history_date', 'history_change_reason',
                    'history_user_id', 'history_type',
                ]
                for field_name in history_field_names:
                    try:
                        value = getattr(instance, field_name)
                        ret[field_name] = value
                    except Exception:  # noqa: pylint=broad-except
                        continue

                for field in fields:
                    try:
                        attribute = field.get_attribute(instance)
                    except Exception:  # noqa: pylint=broad-except
                        continue
                    try:
                        value = field.to_representation(attribute)
                        ret[field.field_name] = value
                    except Exception:  # noqa: pylint=broad-except
                        continue

                return ret

        kwargs['context'] = self.get_serializer_context()
        return HistorySerializer(*args, **kwargs)

    def filter_history_queryset(self, queryset):
        class AutoFilterSet(filterset.FilterSet):
            class Meta(object):
                model = queryset.model
                fields = {
                    'history_id': ['exact', 'gt', 'gte', 'lt', 'lte', 'in'],
                    'history_type': ['exact', 'in'],
                    'history_user_id': ['exact', 'in', 'isnull'],
                    'history_date': ['exact', 'gt', 'gte', 'lt', 'lte', 'in'],
                    self.lookup_field: [
                        'exact', 'gt', 'gte', 'lt', 'lte', 'in', 'isnull'],
                }

        query_params = self.request.query_params.copy()
        if self.lookup_url_kwarg and self.lookup_url_kwarg in query_params:
            query_params[self.lookup_field] = query_params[
                self.lookup_url_kwarg]
            del query_params[self.lookup_url_kwarg]

        return AutoFilterSet(
            query_params, queryset=queryset,
            request=self.request).qs

    def has_history_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        opts = self.get_queryset().model._meta  # noqa: pylint=protected-access
        return (request.user.has_perm(
            f'{opts.app_label}.view_historical{opts.model_name}'))

    @action(methods=['GET'], detail=False)
    def history(self, request, **kwargs):
        if not self.allow_history:
            self.permission_denied(
                request,
                message='You do not have permission to view objects history'
            )

        if not self.has_history_permission(request):
            self.permission_denied(
                request, message='Access denied'
            )

        model_history = self.filter_history_queryset(
            self.get_queryset().model.history.all())
        page = self.paginate_queryset(model_history)
        if page is not None:
            serializer = self.get_history_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_history_serializer(model_history, many=True)
        return Response(serializer.data)
