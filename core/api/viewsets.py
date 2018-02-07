from collections import OrderedDict

from django_filters import filterset
from rest_framework import generics, mixins
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from core.api.mixins import BulkCreateModelMixin


class HistoryViewSetMixin:
    def get_history_serializer(self, *args, **kwargs):
        class HistorySerializer(self.get_serializer_class()):
            def to_representation(self, instance):
                """
                Object instance -> Dict of primitive datatypes.
                """
                ret = OrderedDict()
                fields = self._readable_fields

                field_names = [
                    'history_id', 'history_date', 'history_change_reason',
                    'history_user_id', 'history_type',
                ]
                for field_name in field_names:
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
        # TODO (pahaz): Use this as default permission check for all APIs
        opts = self.get_queryset().model._meta  # noqa: pylint=protected-access
        method = request.method.lower()
        codename = f'can_{method}_api_{opts.model_name}_{self.action}'
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    @list_route(methods=['GET'])
    def history(self, request, **kwargs):
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


class StandartizedGenericViewSet(ViewSetMixin, generics.GenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass


class StandartizedReadOnlyModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    StandartizedGenericViewSet
):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class StandartizedModelViewSet(
    BulkCreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    StandartizedGenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
