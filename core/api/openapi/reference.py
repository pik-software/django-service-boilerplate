from rest_framework.schemas.openapi import SchemaGenerator
from rest_framework.schemas.openapi import AutoSchema
# TODO: klimenkoas: Drop `drf_yasg` dependency
from drf_yasg.utils import get_serializer_ref_name


# This module provides two classes used for nested serializers openapi schema
# reference ($ref) processing.
# Builtin DRF openapi schema generation tool processes each view through its'
# own `AutoSchema` instance, so the only way of processing references is adding
# marks to result schema and reducing them on the final stage within
# `SchemaGenerator.get_schema`.


class ReferenceAutoSchema(AutoSchema):
    """Marks nested serializer schemas with `x-ref` and `x-ref-source` which
    have to be processed later by `RefSchemaGenerator`"""

    def _map_serializer(self, serializer):
        schema = super()._map_serializer(serializer)
        schema['x-ref'] = get_serializer_ref_name(serializer)

        # Marking non-nested serializer
        if not serializer.parent:
            schema['x-ref-source'] = True
        return schema


class ReferenceSchemaGenerator(SchemaGenerator):
    """Reduces nested serializer schemas marked with `x-ref` and
    `x-ref-source` by `ReferenceAutoSchema`"""

    def __init__(self, *args, **kwargs):
        self._ref_definitions = {}
        super().__init__(*args, **kwargs)

    def get_schema(self, *args, **kwargs):  # noqa: arguments-differ
        schema = super().get_schema(*args, **kwargs)
        if schema:
            self._process_schema_refs(schema)
            schema['components'] = {'schemas': self._ref_definitions}
        return schema

    def _process_schema_refs(self, schema):
        """Finds, stores and replaces marked nested serializers with
        references `anyOf.$ref`

        1. Finds schema containing `x-ref`,
        2. Stores such schema in `_definitions`, if
            2.1 definition is missing,
            2.2 marked with `x-ref-source`.
        3. Replaces source schema with `anyOf.[$ref]`.
        4. Moves `title`, `description` values to the field definition
        from the nested schema.
        """

        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = self._process_schema_refs(value)

        if 'x-ref' in schema:
            ref = schema.pop('x-ref')

            # `x-ref-source` marked schema is preffered to be used as
            # definition
            if 'x-ref-source' in schema:
                schema.pop('x-ref-source')
                self._ref_definitions[ref] = schema
            elif ref not in self._ref_definitions:
                self._ref_definitions[ref] = schema

            kwargs = {field: schema.get(field)
                      for field in ['title', 'description']
                      if field in schema}
            schema = {'anyOf': [{'$ref': f'#/components/schemas/{ref}'}],
                      **kwargs}

        return schema
