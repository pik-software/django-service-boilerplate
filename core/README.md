# How-To create new module (API + Admin) #

You can view example here: `contacts`

## settings ##

1. install `requirements.txt`:

```
# HISTORY
django-simple-history==1.9.0

# API
djangorestframework
djangorestframework-filters
django-filter
django-crispy-forms
markdown
coreapi
openapi_codec
drf_openapi
```

1. update `settings.py`:

```
INSTALLED_APPS = [
    ...
    # HISTORY
    'simple_history',
    ...
    # API
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'crispy_forms',  # sexy django_filters forms
    'drf_openapi',
    ...
]
...

MIDDLEWARE = [
    ...
    'simple_history.middleware.HistoryRequestMiddleware',
    ...
]
...

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS':
        'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_METADATA_CLASS': 'core.api.inspectors.StandardizedSimpleMetadata',
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.URLPathVersioning',

    # Generic view behavior
    'DEFAULT_PAGINATION_CLASS': 'core.api.pagination.StandardizedPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'core.api.filters.StandardizedFieldFilters',
        'core.api.filters.StandardizedSearchFilter',
        'core.api.filters.StandardizedOrderingFilter',
    ),

    # Schema
    'DEFAULT_SCHEMA_CLASS': 'core.api.openapi.StandardizedAutoSchema',
    'EXCEPTION_HANDLER': 'core.api.exception_handler.standardized_handler',

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
```

## models ##

1. check `models.py`:

```
from django.db import models
from django.utils.translation import ugettext as _

from pik.core.models import BasePHistorical

class <Organization>(BasePHistorical):
    name = models.CharField(_(<'Наименование'>), max_length=255)
    ...

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['-created']
        verbose_name = _(<'организация'>)
        verbose_name_plural = _(<'организации'>)
```

## admin interface ##

1. check `admin.py` (optional):

```
@admin.register(<Organization>)
class <Organization>Admin(SecureVersionedModelAdmin):
    list_display = (
        'name', ...)
    list_display_links = (
        'name', ...)
    list_select_related = (
        ...)
    search_fields = (
        'name', ...)
    date_hierarchy = 'created'
    list_filter = (...)

    fieldsets = ((
        None,
        {'fields': (
            'suid', 'name', ...)}
    ), (
        _(<'Контакты'>),
        {'fields': (...)})
    )

    inlines = [...]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if request.user.has_perm(<"can_edit_organization">):
            fields.remove('name')
            ...
        ...
        return fields

    def get_queryset(self, request):
        return super().get_queryset(request)
```

## API ##

1. create `api/serializers.py`:

```
class <Organization>Serializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()

    def get__uid(self, obj):  # noqa: pylint: no-self-use
        return obj.uid

    def get__type(self, obj):  # noqa: pylint: no-self-use
        return ContentType.objects.get_for_model(type(obj)).model

    class Meta:
        model = <Organization>
        fields = (
            '_uid', '_type', 'name', ...
        )
 ```

1. create `api/filters.py`:

```
import rest_framework_filters as filters

from <module>.models import <Organization>


NAME_FILTERS = ['exact', 'in', 'startswith', 'endswith', 'contains']


class <Organization>Filter(filters.FilterSet):
    class Meta:
        model = Organization
        fields = {
            'name': NAME_FILTERS,
            ...
        }
```

1. create `api/viewsets.py`

```
from core.api.filters import StandardizedFieldFilters, \
    StandardizedSearchFilter, StandardizedOrderingFilter
from core.api.viewsets import HistoryViewSetMixin, \
    StandartizedReadOnlyModelViewSet

class <Organization>ViewSet(HistoryViewSetMixin, StandartizedReadOnlyModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-id'
    serializer_class = <Organization>Serializer

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = <Organization>Filter
    search_fields = (
        'name', ...)
    ordering_fields = (
        'name', ...)

    def get_queryset(self):
        return <Organization>.objects.all()
```

1. update `urls.py`

```
from core.api.router import StandardizedRouter
from core.api.schema import SchemaView
from core.api.auth import OBTAIN_AUTH_TOKEN
from <module>.api.viewsets import <Organization>ViewSet

router = StandardizedRouter()  # noqa: pylint: invalid-name
router.register(
    <'<organization>-list'>, <Organization>ViewSet, base_name=<'organization'>)
...

urlpatterns = [  # noqa: pylint: invalid-name
    ...
    url(r'^api/v(?P<version>[1-9])/schema/', SchemaView.as_view(), name='api_schema'),
    url(r'^api/v(?P<version>[1-9])/', include(router.urls, namespace='api')),
    url(r'^api-token-auth/', OBTAIN_AUTH_TOKEN),
    ...
]
```

## app level settings ##

1. Setup permissions in /admin/ for API users

# Links

 - how-to update api verion: https://github.com/limdauto/drf_openapi/tree/master/examples
