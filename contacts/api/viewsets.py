from contacts.models import Contact
from core.api.filters import StandardizedFieldFilters, \
    StandardizedSearchFilter, StandardizedOrderingFilter
from core.api.viewsets import HistoryViewSetMixin, StandartizedModelViewSet

from .filters import ContactFilter
from .serializers import ContactSerializer


class ContactViewSet(HistoryViewSetMixin, StandartizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-id'
    serializer_class = ContactSerializer

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = ContactFilter
    search_fields = (
        'name', 'phones', 'emails')
    ordering_fields = ('name', 'order_index')

    def get_queryset(self):
        return Contact.objects.all()
