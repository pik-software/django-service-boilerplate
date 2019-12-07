from pprint import pprint

from rest_framework import status

from core.tests.utils import add_permissions
from ..models import Entity
from ..tests.factories import EntityFactory


def _assert_api_object_list(res, result):
    data = res.json()['results']
    pprint(data)
    assert data == result


def _assert_api_object(res, result):
    data = res.json()
    pprint(data)
    assert data == result


def test_api_try_to_get_unknown_type(api_client):
    res = api_client.get(f'/api/v1/randomname-list/')
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_api_retrieve_list(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [
        {
            '_uid': str(obj.uid),
            '_type': obj.type.slug,
            '_version': obj.version,
            'created': obj.created.isoformat(),
            'updated': obj.updated.isoformat(),
            'foo': 1,
            'bar': obj.value['bar'],
        }
    ])


def test_api_retrieve_object(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res, {
        '_uid': str(obj.uid),
        '_type': obj.type.slug,
        '_version': obj.version,
        'created': obj.created.isoformat(),
        'updated': obj.updated.isoformat(),
        'foo': 1,
        'bar': obj.value['bar'],
    })
