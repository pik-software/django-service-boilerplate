import rest_framework_filters as filters

from core.api.filters import StandardizedModelFilter
from ..models import Contact, Comment, Category

NAME_FILTERS = ['exact', 'in', 'startswith', 'endswith', 'contains']


class CharArrayFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass


class CategoryFilter(StandardizedModelFilter):
    name = filters.AutoFilter(lookups=NAME_FILTERS)

    class Meta(StandardizedModelFilter.Meta):
        model = Category


class ContactFilter(StandardizedModelFilter):
    phones__contains = CharArrayFilter(
        field_name='phones', lookup_expr='contains')
    emails__contains = CharArrayFilter(
        field_name='emails', lookup_expr='contains')
    name = filters.AutoFilter(lookups=NAME_FILTERS)

    class Meta(StandardizedModelFilter.Meta):
        model = Contact


class CommentFilter(StandardizedModelFilter):
    message = filters.AutoFilter(lookups=NAME_FILTERS)
    user = filters.AutoFilter(lookups=['exact', 'in'])

    class Meta(StandardizedModelFilter.Meta):
        model = Comment
