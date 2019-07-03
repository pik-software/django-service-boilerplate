from freezegun import freeze_time
from rest_framework import status

from core.tests.utils import add_permissions
from .factories import EntityFactory
from ..models import Entity


def test_api_filter_by_updated(api_user, api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    add_permissions(api_user, Entity, 'view')
    with freeze_time("2012-01-14"):
        EntityFactory.create(type=obj.type)
        obj = EntityFactory.create(type=obj.type)
    with freeze_time("2013-01-14"):
        EntityFactory.create(type=obj.type)
        obj.value['foo'] = 2
        obj.save()
    EntityFactory.create()

    res = api_client.get(f'/api/v1/{obj.type.slug}-list/')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 4

    filter_date = '2012-04-12T22:33:45.028342'
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?updated__gte={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'/api/v1/{obj.type.slug}-list/?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1
