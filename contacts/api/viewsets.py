from contacts.models import Contact, Comment
from core.api.filters import StandardizedFieldFilters, \
    StandardizedSearchFilter, StandardizedOrderingFilter
from core.api.viewsets import HistoryViewSetMixin, StandardizedModelViewSet

from .filters import ContactFilter, CommentFilter
from .serializers import ContactSerializer, CommentSerializer


class ContactViewSet(HistoryViewSetMixin, StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-id'
    serializer_class = ContactSerializer
    allow_bulk_create = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = ContactFilter
    search_fields = (
        'name', 'phones', 'emails')
    ordering_fields = ('name', 'order_index')

    def get_queryset(self):
        return Contact.objects.all()


class CommentViewSet(HistoryViewSetMixin, StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = CommentSerializer
    allow_bulk_create = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = CommentFilter
    search_fields = (
        'message', 'user')
    ordering_fields = ()

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
