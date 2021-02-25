from functools import partial

from django.conf import settings
from rest_framework.management.commands.generateschema import (
    Command as DRFCommand)
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.settings import perform_import

from core.api.openapi.openapi import StandardizedSchemaGenerator
from core.api.openapi.renders import JSONOpenAPILazyObjRenderer


class Command(DRFCommand):
    urlpatterns = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--urlpatterns', dest="urlpatterns",
                            default='_project_.urls.api_urlpatterns', type=str)

    def handle(self, *args, **options):
        options['title'] = options['title'] or f'{settings.SERVICE_TITLE} API'
        options['description'] = (options['description']
                                  or settings.SERVICE_DESCRIPTION)
        self.urlpatterns = perform_import(
            options['urlpatterns'], '--urlpatterns')
        return super().handle(*args, **options)

    def get_renderer(self, format):  # noqa: redefined-builtin
        renderer = super().get_renderer(format)
        if isinstance(renderer, JSONOpenAPIRenderer):
            return JSONOpenAPILazyObjRenderer()
        return renderer

    def get_generator_class(self):
        generator_class = StandardizedSchemaGenerator
        version = settings.SERVICE_RELEASE

        return partial(
            generator_class, version=version, patterns=self.urlpatterns)
