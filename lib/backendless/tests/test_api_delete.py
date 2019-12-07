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


def test_api_delete_object_by_anon(anon_api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    res = anon_api_client.delete(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_delete_object_without_permission(api_client):  # noqa: pylint=invalid-name
    obj = EntityFactory.create()
    res = api_client.delete(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_delete_object(api_user, api_client):
    obj = EntityFactory.create()
    count0 = Entity.objects.count()
    add_permissions(api_user, Entity, 'delete')
    res = api_client.delete(
        f'/api/v1/{obj.type.slug}-list/{obj.pk}/')
    assert res.status_code == status.HTTP_204_NO_CONTENT
    assert Entity.objects.count() == count0 -1
