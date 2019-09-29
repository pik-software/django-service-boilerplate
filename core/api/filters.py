import coreapi
import rest_framework_filters as rest_filters
from rest_framework_filters.backends import RestFrameworkFilterBackend
from django.db.models import DateTimeField
from rest_framework_filters import RelatedFilter, AutoFilter, FilterSet, \
    IsoDateTimeFilter
# https://github.com/philipn/django-rest-framework-filters/
# commit/379e36359b90658fe10e319c5f3cb232556d8a87
from rest_framework.filters import SearchFilter, OrderingFilter


UID_LOOKUPS = ('exact', 'in', 'isnull')
STRING_LOOKUPS = ('exact', 'in', 'isnull', 'startswith', 'endswith', 'contains')
DATE_LOOKUPS = ('exact', 'in', 'isnull', 'lt', 'gt', 'lte', 'gte')
BOOLEAN_LOOKUPS = ('exact', 'in', 'isnull')
ARRAY_LOOKUPS = ('contains', 'contained_by', 'overlap', 'len', 'isnull')


class StandardizedFieldFilters(RestFrameworkFilterBackend):
    def get_schema_fields(self, view):
        # This is not compatible with widgets where the query param differs
        # from the filter's attribute name. Notably, this includes
        # `MultiWidget`, where query params will be of
        # the format `<name>_0`, `<name>_1`, etc...

        filter_class = getattr(view, 'filter_class', None)
        if filter_class is None:
            try:
                filter_class = self.get_filter_class(view, view.get_queryset())
            except Exception:  # noqa
                raise RuntimeError(
                    f"{view.__class__} is not compatible with "
                    f"schema generation"
                )

        fields = []

        return self.get_flatten_schema_fields('', fields, filter_class)

    def get_flatten_schema_fields(self, prefix, filters: list, filter_class):
        for field_name, field in filter_class.get_filters().items():
            if isinstance(field, RelatedFilter):
                self.get_flatten_schema_fields(
                    prefix + field_name + '__', filters, field.filterset)
            else:
                filters.append(coreapi.Field(
                    name=prefix + field_name,
                    required=False,
                    location='query',
                    schema=self.get_coreschema_field(field)
                ))
        return filters


class StandardizedSearchFilter(SearchFilter):
    pass


class StandardizedOrderingFilter(OrderingFilter):
    pass


class StandardizedModelFilter(FilterSet):
    uid = AutoFilter(lookups=UID_LOOKUPS)
    updated = AutoFilter(lookups=DATE_LOOKUPS)
    created = AutoFilter(lookups=DATE_LOOKUPS)

    class Meta:
        model = None
        fields = {}
        filter_overrides = {
            DateTimeField: {'filter_class': IsoDateTimeFilter}
        }
