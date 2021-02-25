from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, CursorPagination


class StandardizedCursorPagination(CursorPagination):

    page_size_query_param = 'page_size'
    page_size = 20
    max_page_size = 1000


class StandardizedPagination(PageNumberPagination):
    """
    Example: http://api.example.org/accounts/?page=4&page_size=100

    Add this to `settings.py`:

        REST_FRAMEWORK = {
            ...
            'DEFAULT_PAGINATION_CLASS':
                'core.api.pagination.StandardizedPagination',
            ...
        }
    """
    page_size_query_param = 'page_size'
    page_size = 20
    max_page_size = 1000

    def get_next_link(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return page_number

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        return page_number

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('pages', self.page.paginator.num_pages),
            ('page_size', self.page.paginator.per_page),
            ('page', self.page.number),
            ('page_next', self.get_next_link()),
            ('page_previous', self.get_previous_link()),
            ('results', data),
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer', 'example': 123},
                'page': {'type': 'integer'},
                'page_size': {'type': 'integer'},
                'pages': {'type': 'integer'},
                'page_next': {'type': 'integer', 'nullable': True},
                'page_previous': {'type': 'integer', 'nullable': True},
                'results': schema,
            }
        }

    def get_schema_fields(self, view):  # noqa: pylint=useless-super-delegation
        return super().get_schema_fields(view)
