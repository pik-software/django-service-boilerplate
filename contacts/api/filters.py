import rest_framework_filters as filters

from contacts.models import Contact


NAME_FILTERS = ['exact', 'in', 'startswith', 'endswith', 'contains']


class CharArrayFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass


class ContactFilter(filters.FilterSet):
    phones__contains = CharArrayFilter(name='phones', lookup_expr='contains')
    emails__contains = CharArrayFilter(name='emails', lookup_expr='contains')

    class Meta:
        model = Contact
        fields = {
            'name': NAME_FILTERS,
        }
