from random import randint

from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from core.tests.utils import add_permissions
from .factories import EntityFactory
from ..models import Entity

REQUIRED_FIELD_ERROR = {
    'code': 'required',
    'message': ErrorDetail(string='this field is required', code='required')}
INVALID_FIELD_ERROR = {
    'code': 'invalid',
    'message': ErrorDetail(string='this field is not an integer',
                           code='invalid')}


def test_api_create_object_by_anon(anon_api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    data = {}
    res = anon_api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_update_object_without_permission(api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    data = {}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_update_object_without_foo(api_user, api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'change')
    data = {}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        '_uid': obj.pk,
        '_type': obj.type.slug,
        '_version': 2,
        'created': res.data['created'],
        'updated': res.data['updated'],
        'foo': obj.value['foo'],
        'bar': obj.value['bar'],
    }


def test_api_update_object_with_wrong_foo(api_user, api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'change')
    data = {'foo': get_random_string()}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'foo': [INVALID_FIELD_ERROR]},
        'message': 'Invalid input.'}


def test_api_update_object_with_extra_field(api_user, api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'change')
    data = {'foo': randint(100, 200), 'bar': 1000, 'buz': 77}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        '_uid': res.data['_uid'],
        '_type': obj.type.slug,
        '_version': 2,
        'created': res.data['created'],
        'updated': res.data['updated'],
        'foo': data['foo'],
        'bar': data['bar'],
    }

    obj = Entity.objects.get(pk=res.data['_uid'])
    assert obj.value == {'foo': data['foo'], 'bar': 1000}


def test_api_update_object(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'change')
    data = {'foo': 8}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code == status.HTTP_200_OK


def test_api_update_complex_object(api_user, api_client):
    schema = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            'phones': {'type': 'array', 'items': {'type': 'string'}},
            'name': {'type': 'string', 'maxLength': 255, 'minLength': 1},
        }
    }

    obj = EntityFactory.create(type__schema=schema, value={
        'name': 'n', 'phones': ['001']})
    add_permissions(api_user, Entity, 'change')
    data = {'name': 'test', 'phones': ['+7902922992'], 'foo': 22}
    res = api_client.patch(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/', data=data)
    assert res.status_code == status.HTTP_200_OK

    obj = Entity.objects.get(pk=res.data['_uid'])
    assert obj.value == {'name': 'test', 'phones': ['+7902922992']}
