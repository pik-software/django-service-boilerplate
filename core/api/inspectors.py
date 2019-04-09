from collections import OrderedDict

from deprecated import deprecated
from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from rest_framework.metadata import SimpleMetadata
from rest_framework.schemas import AutoSchema

from .pagination import StandardizedPagination, StandardizedCursorPagination


@deprecated
class StandardizedAutoSchema(AutoSchema):
    """
    Add this to `settings.py`:

        REST_FRAMEWORK = {
            ...
            'DEFAULT_SCHEMA_CLASS':
                'core.api.inspectors.StandardizedAutoSchema',
            ...
        }

    """


@deprecated
class StandardizedMetadata(SimpleMetadata):
    """
    Add this to `settings.py`:

        REST_FRAMEWORK = {
            ...
            'DEFAULT_METADATA_CLASS':
                'core.api.inspectors.StandardizedMetadata',
            ...
        }

    """


class StandardizedPaginationInspector(PaginatorInspector):
    def get_paginated_response(self, paginator, response_schema):
        paged_schema = None
        if isinstance(paginator, StandardizedPagination):
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('count', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('page', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('page_size', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('pages', openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ('page_next', openapi.Schema(
                        type=openapi.TYPE_INTEGER, x_nullable=True)),
                    ('page_previous', openapi.Schema(
                        type=openapi.TYPE_INTEGER, x_nullable=True)),
                    ('results', response_schema),
                )),
                required=['results', 'count', 'page', 'page_size']
            )
        elif isinstance(paginator, StandardizedCursorPagination):
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('next', openapi.Schema(
                        type=openapi.TYPE_STRING, x_nullable=True)),
                    ('previous', openapi.Schema(
                        type=openapi.TYPE_STRING, x_nullable=True)),
                    ('results', response_schema),
                )),
                required=['results']
            )

        return paged_schema
