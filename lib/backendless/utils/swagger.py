from collections import defaultdict
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _
from swagger_parser import SwaggerParser


def _merge_keys_to(d1, d2, union=False):
    for k in d1.keys():
        if isinstance(d1[k], dict):
            _merge_keys_to(d1[k], d2.get(k, {}), union=union)
        else:
            d1[k] = d2.get(k, d1[k])
    if union:
        for k in d2.keys():
            if k in d1:
                continue
            if isinstance(d2[k], dict):
                d1[k] = d1.get(k, {})
                _merge_keys_to(d1[k], d2[k], union=union)
            else:
                d1[k] = d2[k]


def check_schema(schema):
    data = {'swagger': '2.0', 'paths': {}, 'definitions': {'Entity': schema},
            'info': {'title': '', 'version': '1'}}
    SwaggerParser(swagger_dict=data)
    return True


def convert_data_to_schema(data, schema):
    data1 = {'swagger': '2.0', 'paths': {}, 'definitions': {'Entity': schema},
             'info': {'title': '', 'version': '1'}}
    parser = SwaggerParser(swagger_dict=data1)
    example = parser.definitions_example['Entity']
    _merge_keys_to(example, data)
    return example


def validate_and_update_schema(schema, schema_ext):
    if not schema:
        return deepcopy(schema_ext)
    check_schema(schema)
    check_schema(schema_ext)
    if schema.get('type') != 'object' or schema_ext.get('type') != 'object':
        raise ValueError('Wrong swagger schema["type"] != "object"')

    result = deepcopy(schema_ext)
    _merge_keys_to(result, schema, union=True)
    return result


def validate_data_by_schema(data, schema, partial=False):
    if schema.get('type') != 'object':
        raise ValueError('invalid schema definition')
    ret = {}
    errors = defaultdict(list)
    required = schema.get('required')
    properties = schema.get('properties')
    if required and not partial:
        for field in required:
            if field not in data:
                err = _('this field is required')
                err.code = 'required'
                errors[field].append(err)
    for field, options in properties.items():
        if options.get('readOnly') or field not in data:
            continue
        if options.get('type'):
            # TODO(pahaz): refactor it!
            if options.get('type') == 'integer' and data.get(field) and \
                    not isinstance(data.get(field), int):
                err = _('this field is not an integer')
                err.code = 'invalid'
                errors[field].append(err)
        ret[field] = data[field]
    return ret, errors
