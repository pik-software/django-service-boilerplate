from django.db.models import DateTimeField
from rest_framework_filters import (
    AutoFilter, FilterSet, IsoDateTimeFilter)


class HistoryFilterBase(FilterSet):
    LOOKUP_FIELD_FILTERS = ('exact', 'gt', 'gte', 'lt', 'lte', 'in', 'isnull')
    history_id = AutoFilter(lookups=('exact', 'gt', 'gte', 'lt', 'lte', 'in'))
    history_type = AutoFilter(lookups=('exact', 'in'))
    history_user_id = AutoFilter(lookups=('exact', 'in', 'isnull'))
    history_date = AutoFilter(lookups=('exact', 'gt', 'gte', 'lt', 'lte', 'in'))

    class Meta:
        model = None
        filter_overrides = {
            DateTimeField: {'filter_class': IsoDateTimeFilter}}


def get_history_filter_class(model_name, viewset):
    name = f'{model_name}FilterSet'

    lookup_filter_name = viewset.lookup_field
    if viewset.lookup_url_kwarg:
        lookup_filter_name = viewset.lookup_url_kwarg

    model = viewset.serializer_class.Meta.model.history.model
    _meta = type("Meta", (HistoryFilterBase.Meta, ), {"model": model})

    lookup_field_filter = AutoFilter(
        field_name=viewset.lookup_field,
        lookups=HistoryFilterBase.LOOKUP_FIELD_FILTERS)

    attrs = {
        lookup_filter_name: lookup_field_filter,
        'Meta': _meta
    }

    return type(name, (HistoryFilterBase, ), attrs)
