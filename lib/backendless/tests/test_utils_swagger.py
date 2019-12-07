from pytest import raises

from ..models import DEFAULT_SCHEMA
from ..utils.swagger import _check_schema, convert_data_to_schema, \
    validate_and_merge_schemas, validate_data_by_schema


def test_check_empty_schema():
    assert _check_schema({})


def test_check_contact_schema():
    assert _check_schema({
        'type': 'object',
        'required': ['name'],
        'title': 'Contact',
        'properties': {
            '_uid': {'title': ' uid', 'type': 'string', 'format': 'uuid',
                     'readOnly': True},
            '_type': {'title': ' type', 'type': 'string', 'readOnly': True},
            '_version': {
                'title': ' version', 'type': 'integer',
                'readOnly': True},
            'created': {'title': 'Создан', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'updated': {'title': 'Updated', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'name': {
                'title': 'Наименование', 'type': 'string',
                'maxLength': 255, 'minLength': 1},
            'phones': {
                'type': 'array',
                'description': 'Номера телефонов вводятся в произвольном '
                               'формате через запятую',
                'items': {
                    'title': 'Phones', 'type': 'string',
                    'maxLength': 30, 'minLength': 1}},
            'emails': {
                'type': 'array',
                'description': 'E-mail адреса вводятся через запятую',
                'items': {
                    'title': 'Emails', 'type': 'string',
                    'format': 'email', 'maxLength': 254, 'minLength': 1}},
            'order_index': {
                'title': 'Индекс для сортировки', 'type': 'integer',
                'maximum': 2147483647, 'minimum': -2147483648}
        }
    })


def test_check_schema_with_skip_ref_check():
    assert _check_schema({
        'type': 'object',
        'required': ['name'],
        'properties': {
            'obj': {'$ref': f'#/definitions/contact'},
            'name': {'type': 'string'},
        }
    }, skip_ref_check=True)


def test_check_default_schema():
    assert _check_schema(DEFAULT_SCHEMA)


def test_check_schema_without_required_field():
    with raises(ValueError):
        _check_schema({
            'type': 'object',
            'required': ['phone'],
            'properties': {
                '_uid': {'title': ' uid', 'type': 'string', 'format': 'uuid',
                         'readOnly': True},
                'name': {
                    'title': 'Наименование', 'type': 'string',
                    'maxLength': 255, 'minLength': 1},
            }
        })


def test_convert_data_to_schema():
    data = {'_uid': 'x', 'foo': 1, 'y': {'x': [1]}}
    res = {'_uid': 'x', 'name': None}
    assert res == convert_data_to_schema(data, {
        'type': 'object',
        'required': ['_uid'],
        'properties': {
            '_uid': {'title': ' uid', 'type': 'string'},
            'name': {
                'title': 'Наименование', 'type': 'string',
                'maxLength': 255, 'minLength': 1},
        }
    })


def test_convert_empty_data_to_schema():
    data = {}
    res = {'_uid': None, 'name': 'noname'}
    assert res == convert_data_to_schema(data, {
        'type': 'object',
        'required': ['_uid'],
        'properties': {
            '_uid': {'title': ' uid', 'type': 'string'},
            'name': {
                'title': 'Наименование', 'type': 'string', 'default': 'noname',
                'maxLength': 255, 'minLength': 1},
        }
    })


def test_validate_and_update_schema():
    assert validate_and_merge_schemas({}, DEFAULT_SCHEMA) == DEFAULT_SCHEMA

    assert validate_and_merge_schemas(DEFAULT_SCHEMA, DEFAULT_SCHEMA) == \
           DEFAULT_SCHEMA


def test_merge_schema_by_validate_and_update_schema():
    data = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            '_uid': {'title': 'uid', 'type': 'string', 'x-extra': 1},
            'name': {
                'title': 'Наименование', 'type': 'string',
                'maxLength': 250, 'minLength': 2},
        }
    }

    res = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            '_uid': {
                'title': 'uid', 'type': 'string', 'format': 'uuid',
                'readOnly': True, 'x-extra': 1},
            '_type': {
                'title': 'type', 'type': 'string',
                'readOnly': True},
            '_version': {
                'title': 'version', 'type': 'integer',
                'readOnly': True},
            'created': {'title': 'created', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'updated': {'title': 'updated', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'name': {
                'title': 'Наименование', 'type': 'string',
                'maxLength': 250, 'minLength': 2},
        }
    }

    assert validate_and_merge_schemas(data, DEFAULT_SCHEMA) == res


def test_validate_data_by_schema():
    ret, err = validate_data_by_schema({}, {
        'type': 'object',
        'required': ['name'],
        'properties': {
            'name': {'type': 'string'},
        }
    })

    assert err == {'name': ['this field is required']}


def test_validate_data_by_schema_no_add_new_data():
    ret, err = validate_data_by_schema({'foo': 1, 'test': 2, 'bar': 'bar'}, {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
        }
    })

    assert err == {}
    assert ret == {}
