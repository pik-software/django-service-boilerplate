from functools import partial

from django.conf import settings
from rest_framework.management.commands.generateschema import (
    Command as DRFCommand)
from rest_framework.renderers import JSONOpenAPIRenderer

from core.api.openapi.openapi import StandardizedSchemaGenerator
from core.api.openapi.renders import JSONOpenAPILazyObjRenderer


class Command(DRFCommand):
    def get_generator_class(self):
        generator_class = StandardizedSchemaGenerator
        title = f'{settings.SERVICE_TITLE} API'
        description = settings.SERVICE_DESCRIPTION
        version = settings.SERVICE_RELEASE

        return partial(generator_class, title=title, description=description,
                       version=version)

    def get_renderer(self, format):  # noqa: redefined-builtin
        renderer = super().get_renderer(format)
        if isinstance(renderer, JSONOpenAPIRenderer):
            return JSONOpenAPILazyObjRenderer()
        return renderer
