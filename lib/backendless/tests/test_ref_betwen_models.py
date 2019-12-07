from rest_framework import status

from core.tests.utils import add_permissions
from ..models import Entity
from .factories import EntityFactory


def test_api_ref_cases(api_user, api_client):
    add_permissions(api_user, Entity, 'view', 'add')
    obj1 = EntityFactory.create()

    schema = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            'obj': {'$ref': f'#/definitions/{obj1.type.slug}'},
            'name': {'type': 'string'},
        }
    }
    obj2 = EntityFactory.create(type__schema=schema, value={'name': 'test'})

    res = api_client.get(f'/api/v1/{obj1.type.slug}-list/')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1

    res = api_client.get(f'/api/v1/{obj2.type.slug}-list/')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1
    assert res.json()['results'][0] == {
        '_type': obj2.type.slug,
        '_uid': str(obj2.pk),
        '_version': 1,
        'created': obj2.created.isoformat(),
        'updated': obj2.updated.isoformat(),
        'name': 'test',
        'obj': None,
    }

    obj3 = EntityFactory.create(type__schema=schema, value={
        'obj': {'_uid': str(obj1.uid), '_type': obj1.type.slug},
        'name': 'test'})
    res = api_client.get(f'/api/v1/{obj3.type.slug}-list/')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1
    assert res.json()['results'][0] == {
        '_type': obj3.type.slug,
        '_uid': str(obj3.pk),
        '_version': 1,
        'created': obj3.created.isoformat(),
        'updated': obj3.updated.isoformat(),
        'name': 'test',
        'obj': {'_uid': str(obj1.uid), '_type': obj1.type.slug},
    }
