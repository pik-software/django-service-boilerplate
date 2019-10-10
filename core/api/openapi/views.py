from django.views.generic.base import TemplateResponseMixin, ContextMixin
from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings

from core.api.openapi import StandardizedSchemaGenerator


class RedocSchemaViewMixIn(TemplateResponseMixin, ContextMixin):
    """ Adds Redoc schema rendering """

    template_name = 'redoc.html'

    def get(self, request, *args, **kwargs):
        openapi_format = self.request.GET.get('format')
        if not openapi_format or openapi_format == 'redoc':
            context = self.get_context_data(url=f'{request.path}?format=openapi-json', **kwargs)
            return self.render_to_response(context)
        return super().get(request, *args, **kwargs)


class StandardizedSchemaView(RedocSchemaViewMixIn, SchemaView):
    pass


def get_standardized_schema_view(
        title=None, url=None, description=None, urlconf=None,
        renderer_classes=None, public=False, patterns=None,
        generator_class=StandardizedSchemaGenerator,
        authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
        permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES,
        version=None, schema_view_class=StandardizedSchemaView):

    generator = generator_class(
        title=title, url=url, description=description,
        urlconf=urlconf, patterns=patterns, version=version
    )

    return schema_view_class.as_view(
        renderer_classes=renderer_classes,
        schema_generator=generator,
        public=public,
        authentication_classes=authentication_classes,
        permission_classes=permission_classes,
    )
