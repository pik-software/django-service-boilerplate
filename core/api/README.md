# Standardized API CheckList #

 - [ ] Model has: `history = HistoricalRecords()`
 - [ ] Model has: `def __str__(self)`
 - [ ] Model: `issubclass(Model, BasePHistorical)`
 - [ ] Model.Meta: `verbose_name`, `verbose_name_plural`
 - [ ] Model.Meta: `ordering = ['-created']`

 - [ ] `module/api/__init__.py` exists
 - [ ] `module/api/serializers.py` exists
 - [ ] `module/api/filters.py` exists
 - [ ] `module/api/viewsets.py` exists

 - [ ] api.serializers.ModelSerializer: `issubclass(ModelSerializer, StandardizedModelSerializer)`
 - [ ] api.vewsets.ModelViewSet: `issubclass(ModelViewSet, StandardizedModelViewSet)`

```
class ModelViewSet(StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = <ModelSerializer>
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = <ModelFilter>
    search_fields = (...)
    ordering_fields = (...)
```

 - [ ] api.filters.ModelFilter: (optional)

```
class ModelFilter(filters.FilterSet):
    class Meta:
        model = Model
        fields = {
            ...
        }
```

# SCHEMA #

DEFAULT_AUTO_SCHEMA_CLASS
`view.swagger_schema`
`view.method._swagger_auto_schema.auto_schema`
`view.method._swagger_auto_schema[method].auto_schema`
