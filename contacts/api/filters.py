import rest_framework_filters as filters
from django.db.models import DateTimeField

from ..models import Contact, Comment, Category

NAME_FILTERS = ['exact', 'in', 'startswith', 'endswith', 'contains']


class CharArrayFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass


class CategoryFilter(filters.FilterSet):
    name = filters.AutoFilter(lookups=NAME_FILTERS)
    updated = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])
    created = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])

    class Meta:
        model = Category
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }


class ContactFilter(filters.FilterSet):
    phones__contains = CharArrayFilter(
        field_name='phones', lookup_expr='contains')
    emails__contains = CharArrayFilter(
        field_name='emails', lookup_expr='contains')
    name = filters.AutoFilter(lookups=NAME_FILTERS)
    updated = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])
    created = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])

    class Meta:
        model = Contact
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }


class CommentFilter(filters.FilterSet):
    message = filters.AutoFilter(lookups=NAME_FILTERS)
    user = filters.AutoFilter(lookups=['exact', 'in'])
    updated = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])
    created = filters.AutoFilter(lookups=['exact', 'gt', 'gte', 'lt', 'lte'])

    class Meta:
        model = Comment
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }
