import inspect
from urllib.parse import urljoin

from django.utils.translation import ugettext as _
from rest_framework.fields import (
    ChoiceField, MultipleChoiceField, SerializerMethodField)
from rest_framework.serializers import ModelSerializer
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator
# TODO: klimenkoas: Drop `drf_yasg` dependency
from drf_yasg.inspectors.field import get_basic_type_info_from_hint
from drf_yasg.utils import (
    force_real_str, field_value_to_representation, filter_none,
    get_serializer_ref_name)
from drf_yasg.inspectors.field import typing, inspect_signature
from ddtrace.utils.merge import deepmerge

from core.api.openapi.reference import (
    ReferenceAutoSchema, ReferenceSchemaGenerator)


FIELD_MAPPING = (
    ('title', 'label', lambda x: force_real_str(x).strip().capitalize()),
    ('description', 'help_text', force_real_str)
)


SERIALIZER_FIELD_MAPPING = FIELD_MAPPING + (
    ('x-title-plural', 'label_plural', force_real_str),
)


class TypedSerializerAutoSchema(AutoSchema):
    """Adds enum for `serializer._type`"""

    TYPE_FIELD = '_type'

    def _map_serializer(self, serializer):
        schema = super()._map_serializer(serializer)
        properties = schema['properties']
        type_field = serializer.fields.get(self.TYPE_FIELD)
        has_typefield = (isinstance(serializer, ModelSerializer)
                         and isinstance(type_field, SerializerMethodField)
                         and self.TYPE_FIELD in properties)
        if has_typefield:
            type_name = type_field.to_representation(serializer.Meta.model())
            if type_name:
                properties[self.TYPE_FIELD]['enum'] = [type_name.lower()]
        return schema


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

        is_deprecated = getattr(getattr(serializer, 'Meta', None),
                                'deprecated', False)

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


class SerializerMethodFieldAutoSchema(AutoSchema):
    """ Provides `SerializerMethodField` property types by
    python typing introspection """

    # TODO: klimenko add Serializer handling inside SerializerMethodField
    def _map_field(self, field):
        schema = super()._map_field(field)
        supports_signing = typing and inspect_signature
        if isinstance(field, SerializerMethodField) and supports_signing:
            method = getattr(field.parent, field.method_name)
            hint_class = inspect_signature(method).return_annotation
            if (not inspect.isclass(hint_class)
                    and hasattr(hint_class, '__args__')):
                hint_class = hint_class.__args__[0]  # noqa: protected-access
            if (inspect.isclass(hint_class)
                    and not issubclass(hint_class, inspect._empty)):  # noqa: protected-access
                type_info = get_basic_type_info_from_hint(hint_class)
                schema.update(filter_none(type_info))
        return schema


class ListFiltersOnlyAutoSchema(AutoSchema):
    """ Removes filters for non list view actions

        Overriding default DRF
    """

    def _allows_filters(self, path, method):
        if hasattr(self.view, 'action') and self.view.action not in ["list"]:
            return False
        return super()._allows_filters(path, method)


class CustomizableSerializerAutoSchema(AutoSchema):
    def _map_serializer(self, serializer):
        result = super()._map_serializer(serializer)
        if hasattr(serializer.Meta, 'update_schema'):
            result = deepmerge(result, serializer.Meta.update_schema)
        return result


class OperationSummaryAutoSchema(AutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        serializer = self.view.get_serializer(method, path)
        summary = None
        if operation['operationId'].startswith('list'):
            summary = _('Список объектов {serializer.label_plural}')
        if operation['operationId'].startswith('retrieve'):
            summary = _('Получить объект {serializer.label}')
        if operation['operationId'].startswith('create'):
            summary = _('Заменить объект {serializer.label}')
        if operation['operationId'].startswith('update'):
            summary = _('Изменить объект {serializer.label}')
        if operation['operationId'].startswith('partial_update'):
            summary = _('Создать объект {serializer.label}')
        if operation['operationId'].startswith('destroy'):
            summary = _('Удалить объект {serializer.label}')
        if summary:
            operation['summary'] = summary.format(serializer=serializer)
        return operation


class StandardizedAutoSchema(ReferenceAutoSchema,
                             TypedSerializerAutoSchema,
                             EnumNamesAutoSchema,
                             DeprecatedFieldAutoSchema,
                             DeprecatedSerializerAutoSchema,
                             ModelSerializerFieldsAutoSchema,
                             FieldMappingAutoSchema,
                             ListFiltersOnlyAutoSchema,
                             CustomizableSerializerAutoSchema,
                             OperationSummaryAutoSchema,
                             SerializerMethodFieldAutoSchema):
    pass


class CustomizableViewSchemaGenerator(SchemaGenerator):
    def __init__(self, *args, **kwargs):
        self.history_tags = set()
        self.methods_tags = set()
        self.entities_tags = set()
        super().__init__(*args, **kwargs)

    def _add_operation_tags(self, operation, path, view, method):
        serializer = view.schema._get_serializer(path, method)
        self.methods_tags.add(method)
        ref_name = get_serializer_ref_name(serializer)
        tag = ref_name
        if 'historical' in ref_name.lower():
            tag = 'history'
            self.history_tags.add(tag)
        else:
            self.entities_tags.add(ref_name)
        operation['tags'] = [tag, method]

    def _check_view_schema_update(self, view, schema):
        """Checking neighbour view schema patching

        Different view operations are provided on the same level,
        so this method checks weather missing key got patched."""
        for key, value in view.update_schema.items():
            if key not in schema:
                raise Exception(f'View {view} `update_schema`'
                                f' contains redundant key {key}')

    def get_paths(self, request=None):
        result = {}

        paths, view_endpoints = self._get_paths_and_endpoints(request)

        # Only generate the path prefix for paths that will be included
        if not paths:
            return None

        prev_view = None
        view_result = {}
        for path, method, view in view_endpoints:
            if view and view != prev_view and hasattr(view, 'update_schema'):
                self._check_view_schema_update(view, result)
                result.update(deepmerge(view_result, view.update_schema))
                view_result = {}
                prev_view = view

            if not self.has_view_permissions(path, method, view):
                continue
            operation = view.schema.get_operation(path, method)
            self._add_operation_tags(operation, path, view, method)

            # Normalise path for any provided mount url.
            if path.startswith('/'):
                path = path[1:]
            path = urljoin(self.url or '/', path)

            view_result.setdefault(path, {})
            view_result[path][method.lower()] = operation

        if view_result:
            result.update(view_result)

        return result

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema['x-tagGroups'] = [
            {'name': _('Сущности'), 'tags': list(self.entities_tags)},
            {'name': _('Методы'), 'tags': list(self.methods_tags)},
            {'name': _('История'), 'tags': list(self.history_tags)},
        ]
        return schema


class StandardizedSchemaGenerator(CustomizableViewSchemaGenerator,
                                  ReferenceSchemaGenerator):
    pass
