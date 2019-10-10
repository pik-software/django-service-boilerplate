import inspect

from rest_framework.fields import (
    ChoiceField, MultipleChoiceField, SerializerMethodField)
from rest_framework.schemas.openapi import AutoSchema
# TODO: klimenkoas: Drop `drf_yasg` dependency
from drf_yasg.inspectors.field import get_basic_type_info_from_hint
from drf_yasg.utils import (
    force_real_str, field_value_to_representation, filter_none)
from drf_yasg.inspectors.field import typing, inspect_signature

from core.api.openapi.reference import (
    ReferenceAutoSchema, ReferenceSchemaGenerator)


FIELD_MAPPING = (
    ('title', 'label', force_real_str),
    ('description', 'help_text', force_real_str)
)


SERIALIZER_FIELD_MAPPING = FIELD_MAPPING + (
    ('x-title-plural', 'label_plural', force_real_str),
)


class ModelSerializerFieldsAutoSchema(AutoSchema):
    """ Adds serializers title, description and x-title-plural  """

    def _map_serializer(self, serializer):
        schema = super()._map_serializer(serializer)
        for dst, src, method in SERIALIZER_FIELD_MAPPING:
            value = getattr(serializer, src, None)
            if value is not None:
                schema[dst] = method(value)
        return schema


class EnumNamesAutoSchema(AutoSchema):
    """ Adds enumNames for choice fields """

    def _map_field(self, field):
        schema = super()._map_field(field)

        if isinstance(field, ChoiceField):
            enum_values = []
            for choice in field.choices.values():
                if isinstance(field, MultipleChoiceField):
                    choice = field_value_to_representation(field, [choice])[0]
                else:
                    choice = field_value_to_representation(field, choice)

                enum_values.append(choice)
            if enum_values:
                schema['x-enumNames'] = enum_values

        return schema


class DeprecatedFieldAutoSchema(AutoSchema):
    """ Fetches serializer deprecation status from serializer and parent """

    def _map_serializer(self, serializer):
        schema = super()._map_serializer(serializer)

        parent_meta = getattr(serializer.parent, 'Meta', None)
        deprecated = getattr(parent_meta, 'deprecated_fields', {})
        is_deprecated_as_field = deprecated.get(serializer.field_name, False)

        is_deprecated = getattr(serializer.Meta, 'deprecated', False)

        if is_deprecated_as_field or is_deprecated:
            schema['deprecated'] = True
        return schema


class DeprecatedSerializerAutoSchema(AutoSchema):
    """ Fetches fields and serializer deprecation status from parent serializer
    `Meta` class """

    def _map_field(self, field):
        schema = super()._map_field(field)
        _meta = getattr(field.parent, 'Meta', None)
        deprecated = getattr(_meta, 'deprecated_fields', {})
        is_deprecated = deprecated.get(field.field_name, False)
        if is_deprecated:
            schema['deprecated'] = is_deprecated
        return schema


class FieldMappingAutoSchema(AutoSchema):
    """ Fetches field properties from serializer

    Default DRF openapi AutoSchema ignores Fields titles."""

    def _map_field(self, field):
        schema = super()._map_field(field)
        for dst, src, method in FIELD_MAPPING:
            value = getattr(field, src, None)
            if value is not None:
                schema[dst] = method(value)
        return schema


class SerializerMethodFieldAuthSchema(AutoSchema):
    """ Provides `SerializerMethodField` property types by
    python typing introspection """

    # TODO: klimenko add Serializer handling inside SerializerMethodField
    def _map_field(self, field):
        schema = super()._map_field(field)
        supports_signing = typing and inspect_signature
        if isinstance(field, SerializerMethodField) and supports_signing:
            method = getattr(field.parent, field.method_name)
            hint_class = inspect_signature(method).return_annotation
            is_inspectable = (inspect.isclass(hint_class)
                              and not issubclass(hint_class, inspect._empty))  # noqa: protected-access
            if is_inspectable:
                type_info = get_basic_type_info_from_hint(hint_class)
                schema.update(filter_none(type_info))
        return schema


# TODO: klimenkoas add view deprecation status handling
class StandardizedAutoSchema(ReferenceAutoSchema,
                             EnumNamesAutoSchema,
                             DeprecatedFieldAutoSchema,
                             DeprecatedSerializerAutoSchema,
                             FieldMappingAutoSchema,
                             SerializerMethodFieldAuthSchema):
    pass


class StandardizedSchemaGenerator(ReferenceSchemaGenerator):
    pass
