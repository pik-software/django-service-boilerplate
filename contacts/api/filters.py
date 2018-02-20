import rest_framework_filters as filters

from ..models import Contact, Comment

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


class CommentFilter(filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            'message': NAME_FILTERS,
            'user': ['exact', 'in'],
        }
