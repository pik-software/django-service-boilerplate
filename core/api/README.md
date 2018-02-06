# Standardized API CheckList #

 - [ ] Model wrapped by: `@reversion.register()`
 - [ ] Model has: `UID_PREFIX`
 - [ ] Model has: `history = HistoricalRecords()`
 - [ ] Model has: `def __str__(self)`
 - [ ] Model: `issubclass(Model, (Uided, PUided))`
 - [ ] Model: NullOwned, NullOwned, Dated, Versioned, ... (optional)
 - [ ] Model.Meta: `verbose_name`, `verbose_name_plural`
 - [ ] Model.Meta: `ordering = ['-id']` / `ordering = ['-created']`
 - [ ] Model.Meta.permissions has: `can_edit_<model-name>`
 - [ ] Model.Meta.permissions has: `can_get_api_<model-name>_history`

 - [ ] `module/api/__init__.py` exists
 - [ ] `module/api/serializers.py` exists
 - [ ] `module/api/filters.py` exists
 - [ ] `module/api/viewsets.py` exists

 - [ ] module.api.filters.ModelSerializer has: `_uid`, `_type`

```
class ModelSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()

    def get__uid(self, obj):  # noqa: pylint=no-self-use
        return obj.uid

    def get__type(self, obj):  # noqa: pylint=no-self-use
        return ContentType.objects.get_for_model(type(obj)).model

    class Meta:
        model = Model
        fields = (
            '_uid', '_type', ...
        )
```

 - [ ] module.api.filters.ModelFilter exists: (optional)

```
class ModelFilter(filters.FilterSet):
    class Meta:
        model = Model
        fields = {
            ...
        }
```

 - [ ] module.api.vewsets.ModelViewSet:

```
class ModelViewSet(HistoryViewSetMixin, StandartizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-id' / ordering = '-created'
    serializer_class = ContactSerializer

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = ModelFilter
    search_fields = (
        ...)
    ordering_fields = (...)

    def get_queryset(self):
        return Contact.objects.all()

    ...
```

 - [ ] ModelViewSet: `issubclass(ModelViewSet, (StandartizedGenericViewSet, StandartizedReadOnlyModelViewSet, StandartizedModelViewSet))`
 - [ ] ModelViewSet: `issubclass(ModelViewSet, HistoryViewSetMixin)` (optional)
 - [ ] ModelViewSet has: `lookup_field`, `lookup_url_kwarg`, `ordering`, `serializer_class`
 - [ ] ModelViewSet has: `filter_backends = (StandardizedFieldFilters, StandardizedSearchFilter, StandardizedOrderingFilter)`
 - [ ] ModelViewSet has: `filter_class = ModelFilter`
 - [ ] ModelViewSet has: `search_fields`, `ordering_fields`, `get_queryset`
