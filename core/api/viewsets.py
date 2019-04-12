from rest_framework import generics, mixins
from rest_framework.viewsets import ViewSetMixin

from ..api.mixins import BulkCreateModelMixin


class StandardizedGenericViewSet(ViewSetMixin, generics.GenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    select_related_fields = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        return queryset


class StandardizedReadOnlyModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    StandardizedGenericViewSet
):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class StandardizedModelViewSet(
    BulkCreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    StandardizedGenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
