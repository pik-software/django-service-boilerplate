from rest_framework import generics, mixins
from rest_framework.viewsets import ViewSetMixin

from replication.api.mixins import SubscribeViewSetMixin
from ..api.mixins import BulkCreateModelMixin, HistoryViewSetMixin


class StandardizedGenericViewSet(ViewSetMixin, generics.GenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass


class StandardizedReadOnlyModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    SubscribeViewSetMixin,
    HistoryViewSetMixin,
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
    SubscribeViewSetMixin,
    HistoryViewSetMixin,
    StandardizedGenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
