from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from core.api.filters import StandardizedFieldFilters, \
    StandardizedOrderingFilter, StandardizedSearchFilter
from core.api.pagination import StandardizedCursorPagination

from .filters import get_history_filter_class
from .serializers import get_history_serializer_class


class HistoryViewSetBase(ListModelMixin, GenericViewSet):
    pagination_class = StandardizedCursorPagination
    ordering = ('updated', )
    ordering_fields = ('updated', 'uid', )

    serializer_class = None
    filter_class = None

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)

    def get_queryset(self):
        return super().get_queryset().all()


def get_history_viewset(viewset):
    serializer_class = getattr(viewset, 'serializer_class', None)
    queryset = serializer_class.Meta.model.history
    model = queryset.model
    model_name = model._meta.object_name  # noqa: protected-access
    name = f'{model_name}ViewSet'

    serializer_class = get_history_serializer_class(
        model_name, serializer_class)
    filter_class = get_history_filter_class(model_name, viewset)

    return type(name, (HistoryViewSetBase,), {
        'serializer_class': serializer_class,
        'filter_class': filter_class,
        'queryset': queryset
    })
