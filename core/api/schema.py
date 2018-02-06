from drf_openapi.entities import OpenApiSchemaGenerator
from drf_openapi.views import SchemaView as BaseSchemaView
from rest_framework import permissions, response, serializers
from rest_framework.pagination import PageNumberPagination, \
    LimitOffsetPagination, CursorPagination

from core.api.pagination import StandardizedPagination


class _StandardizedOpenApiSchemaGenerator(OpenApiSchemaGenerator):
    def get_paginator_serializer(self, view, child_serializer_class):
        """
        Customized result for `StandardizedPagination`
        """
        class BaseFakeListSerializer(serializers.Serializer):  # noqa: pylint=abstract-method 'create'/'update' is not overridden
            results = child_serializer_class(many=True)

        # Validate if the view has a pagination_class
        has_no_pagination_class = (
            not hasattr(view, 'pagination_class') or
            view.pagination_class is None)
        if has_no_pagination_class:
            return BaseFakeListSerializer

        pager = view.pagination_class
        if hasattr(pager, 'default_pager'):
            # Must be a ProxyPagination
            pager = pager.default_pager

        class FakePrevNextListSerializer(BaseFakeListSerializer):  # noqa: pylint=abstract-method 'create'/'update' is not overridden
            next = serializers.URLField()
            previous = serializers.URLField()

        class FakeListSerializer(FakePrevNextListSerializer):  # noqa: pylint=abstract-method 'create'/'update' is not overridden
            count = serializers.IntegerField()

        class FakeStandardizedPagination(BaseFakeListSerializer):  # noqa: pylint=abstract-method 'create'/'update' is not overridden
            count = serializers.IntegerField()
            pages = serializers.IntegerField()
            page_size = serializers.IntegerField()
            page = serializers.IntegerField()
            page_next = serializers.IntegerField()
            page_previous = serializers.IntegerField()

        if issubclass(pager, StandardizedPagination):
            return FakeStandardizedPagination
        elif issubclass(pager, (PageNumberPagination, LimitOffsetPagination)):
            return FakeListSerializer
        elif issubclass(pager, CursorPagination):
            return FakePrevNextListSerializer

        return BaseFakeListSerializer

    def get_serializer_fields(self, path, method, view, version=None,
                              method_func=None):
        if method in ('PUT', 'PATCH', 'POST'):
            return super().get_serializer_fields(
                path, method, view, version, method_func)
        return []


class SchemaView(BaseSchemaView):
    """
    Auto schema generator! Add this view in `urls.py`

        urlpatterns = [
            ...
            url(r'^api/v(?P<version>[1-9])/schema/',
                SchemaView.as_view(), name='api_schema'),
            ...
        ]
    """
    permission_classes = (permissions.IsAuthenticated, )
    title = 'API Documentation'

    def get(self, request, version):
        generator = _StandardizedOpenApiSchemaGenerator(
            version=version,
            url=self.url,
            title=self.title,
        )
        return response.Response(generator.get_schema(request))
