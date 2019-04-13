import rest_framework_filters as filters
from django.db.models import DateTimeField

from ..models import Contact, Comment

NAME_FILTERS = ['exact', 'in', 'startswith', 'endswith', 'contains']


class CharArrayFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass


class ContactFilter(filters.FilterSet):
    phones__contains = CharArrayFilter(
        field_name='phones', lookup_expr='contains')
    emails__contains = CharArrayFilter(
        field_name='emails', lookup_expr='contains')

    class Meta:
        model = Contact
        fields = {
            'name': NAME_FILTERS,
            'updated': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'created': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }


class CommentFilter(filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            'message': NAME_FILTERS,
            'user': ['exact', 'in'],
            'updated': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'created': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }
