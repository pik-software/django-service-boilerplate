import warnings

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_filters import RelatedFilter, BaseCSVFilter, AutoFilter
from rest_framework.filters import SearchFilter, OrderingFilter


class StandardizedFieldFilters(DjangoFilterBackend):
    def get_schema_operation_parameters(self, view):
        try:
            queryset = view.get_queryset()
        except Exception:  # noqa: broad-except
            queryset = None
            warnings.warn(
                f'{view.__class__} is not compatible with schema generation')

        filterset_class = self.get_filterset_class(view, queryset)
        return self.get_flatten_schema_operation_parameters(filterset_class)

    def get_flatten_schema_operation_parameters(self, filterset_class,
                                                prefix=''):
        if not filterset_class:
            return []
        filters = []

        for field_name, field in filterset_class.base_filters.items():
            if isinstance(field, RelatedFilter):
                filters.extend(self.get_flatten_schema_operation_parameters(
                    field.filterset, f'{prefix}{field_name}__'))
            else:
                filters.append({
                    'name': f'{prefix}{field_name}',
                    'required': field.extra['required'],
                    'in': 'query',
                    'description': str(field.extra.get('help_text', '')),
                    'schema': {
                        'type': 'string'}})
        return filters


class StandardizedSearchFilter(SearchFilter):
    pass


class StandardizedOrderingFilter(OrderingFilter):
    pass


class ArrayFilter(BaseCSVFilter, AutoFilter):
    DEFAULT_LOOKUPS = ['contains', 'contained_by', 'overlap', 'len']

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookups', self.DEFAULT_LOOKUPS)
        super().__init__(*args, **kwargs)
