from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


class StandardizedSchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, request=None, public=False):
        return super().get_schema(request, public)


class StandardizedAutoSchema(SwaggerAutoSchema):

    def get_operation(self, operation_keys):
        return super().get_operation(operation_keys)


def get_standardized_schema_view(
        api_urlpatterns, title="API",
        description="API", default_version='v1'):
    schema_view = get_schema_view(
        openapi.Info(
            title=title,
            description=description,
            default_version=default_version,
        ),
        patterns=api_urlpatterns,
        public=True,
    )
    return schema_view.with_ui('redoc', cache_timeout=0)
