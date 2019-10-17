from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.conf import settings

from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings

from core.api.openapi import StandardizedSchemaGenerator


class RedocSchemaViewMixIn(TemplateResponseMixin, ContextMixin):
    """ Adds Redoc schema rendering """

    template_name = 'redoc.html'

    @method_decorator(login_required)
    def get_redoc(self, request, **kwargs):
        context = self.get_context_data(
            url=f'{request.path}?format=openapi-json', **kwargs)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        """Initiating auth on anon redoc request"""
        openapi_format = self.request.GET.get('format', '')
        if openapi_format in('', 'redoc') and request.method.lower() == 'get':
            return self.get_redoc(request, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class StandardizedSchemaView(RedocSchemaViewMixIn, SchemaView):
    pass


def get_standardized_schema_view(
        title=f'{settings.SERVICE_TITLE} API', url=None,
        description=settings.SERVICE_DESCRIPTION, urlconf=None,
        renderer_classes=None, public=False, patterns=None,
        generator_class=StandardizedSchemaGenerator,
        authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
        permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES,
        version=settings.SERVICE_RELEASE,
        schema_view_class=StandardizedSchemaView):

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
