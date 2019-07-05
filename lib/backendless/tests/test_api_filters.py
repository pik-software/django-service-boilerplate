from freezegun import freeze_time
from rest_framework import status

from core.tests.utils import add_permissions
from .factories import EntityFactory
from ..models import Entity


def test_api_filter_by_updated(api_user, api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    base_url = f'/api/v1/{obj.type.slug}-list/'
    add_permissions(api_user, Entity, 'view')
    with freeze_time("2012-01-14"):
        EntityFactory.create(type=obj.type)
        obj = EntityFactory.create(type=obj.type)
    with freeze_time("2013-01-14"):
        EntityFactory.create(type=obj.type)
        obj.value['foo'] = 2
        obj.save()
    EntityFactory.create()

    res = api_client.get(f'{base_url}?')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 4

    filter_date = '2012-04-12T22:33:45.028342'
    res = api_client.get(f'{base_url}?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'{base_url}?updated__gte={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'{base_url}?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1


def test_api_filter_by_foo(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')
    EntityFactory.create(type=obj.type, value={"foo": 5, "bar": 1500})
    EntityFactory.create(type=obj.type, value={"foo": 5, "bar": 1600})
    EntityFactory.create(type=obj.type, value={"foo": 6, "bar": 1700})
    EntityFactory.create(type=obj.type, value={"foo": 6, "bar": 1800})
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/')
    assert res.json()['count'] == 5

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?foo=5')
    assert res.json()['count'] == 2

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?foo__in=5,6')
    assert res.json()['count'] == 4

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?bar__gte=1700')
    assert res.json()['count'] == 2

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?bar__gt=1700')
    assert res.json()['count'] == 1


def test_api_invalid_filter_by_foo(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?foo__qwe__qq=5')
    assert res.json()['count'] == 0


def test_api_invalid_filter_by_qqq(api_user, api_client):
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?qqq__qwe__qq=5')
    assert res.json()['count'] == 1
