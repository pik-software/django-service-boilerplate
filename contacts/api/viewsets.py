from contacts.models import Contact, Comment, Category
from core.api.filters import StandardizedFieldFilters, \
    StandardizedSearchFilter, StandardizedOrderingFilter
from core.api.viewsets import StandardizedModelViewSet

from .filters import ContactFilter, CommentFilter, CategoryFilter
from .serializers import ContactSerializer, CommentSerializer, \
    CategorySerializer


class ContactViewSet(StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-id'
    serializer_class = ContactSerializer
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = ContactFilter
    search_fields = (
        'name', 'phones', 'emails')
    ordering_fields = ('created', 'updated', 'name', 'order_index')

    def get_queryset(self):
        return Contact.objects.all()


class CommentViewSet(StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = CommentSerializer
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = CommentFilter
    search_fields = (
        'message', 'user')
    ordering_fields = ('created', 'updated')

    def get_queryset(self):
        return Comment.objects.all().select_related('contact')


class CategoryViewSet(StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = CategorySerializer
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = CategoryFilter
    search_fields = (
        'name')
    ordering_fields = ('created', 'updated')

    def get_queryset(self):
        return Category.objects.all()
