import pytest

import django.test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework import status

from core.tasks.fixtures import create_user

from contacts.models import Contact
from contacts.tests.factories import ContactFactory


@pytest.fixture
def logged_user_client(client: django.test.Client):
    user = create_user()
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture(params=[
    (Contact, ContactFactory),
])
def api_history_model_and_factory(request):
    return request.param


def _add_get_api_history_access(user, model):
    model_type_name = ContentType.objects.get_for_model(model).model
    permission = Permission.objects.get(
        codename=f'can_get_api_{model_type_name}_history')
    user.user_permissions.add(permission)


def test_get_api_history_access_denied(  # noqa: pylint=invalid-name
        logged_user_client, api_history_model_and_factory):  # noqa: pylint=redefined-outer-name
    model, factory = api_history_model_and_factory
    factory.create()
    model_type_name = ContentType.objects.get_for_model(model).model

    res = logged_user_client.get(f'/api/v1/{model_type_name}-list/history/')

    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.data == {
        'code': 'permission_denied', 'message': 'Access denied'}


def test_get_api_history_filtered_by_uid(  # noqa: pylint=invalid-name
        logged_user_client, api_history_model_and_factory):  # noqa: pylint=redefined-outer-name
    model, factory = api_history_model_and_factory
    factory.create()
    obj = factory.create()
    model_type_name = ContentType.objects.get_for_model(model).model
    user = logged_user_client.user

    _add_get_api_history_access(user, model)
    res = logged_user_client.get(
        f'/api/v1/{model_type_name}-list/history/?_uid={obj.uid}')

    assert res.status_code == status.HTTP_200_OK
    count = res.data['count']
    first_result = res.data['results'][0]
    assert count == 1
    assert first_result['_uid'] == obj.uid
    assert first_result['_type'] == 'historical' + model_type_name
    assert first_result['history_change_reason'] is None
    assert first_result['history_type'] == "+"


def test_get_api_history(
        logged_user_client, api_history_model_and_factory):  # noqa: pylint=redefined-outer-name
    model, factory = api_history_model_and_factory
    factory.create()
    factory.create()
    model_type_name = ContentType.objects.get_for_model(model).model
    user = logged_user_client.user

    _add_get_api_history_access(user, model)
    res = logged_user_client.get(
        f'/api/v1/{model_type_name}-list/history/')

    assert res.status_code == status.HTTP_200_OK
    assert res.data['count'] == 2
