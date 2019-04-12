from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.views import get_schema_view


class StandardizedSchemaGenerator(OpenAPISchemaGenerator):
    pass


class StandardizedAutoSchema(SwaggerAutoSchema):
    pass


def get_standardized_schema_view(api_urlpatterns):
    schema_view = get_schema_view(
        patterns=api_urlpatterns,
        public=True,
    )
    return schema_view.with_ui('redoc', cache_timeout=1)
