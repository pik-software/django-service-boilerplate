from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {'version': 1}),
    (Comment, CommentFactory, {'version': 1}),
])
def api_model(request):
    return request.param


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture
def api_client():
    user = create_user()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


def _url(model, options):
    _type = ContentType.objects.get_for_model(model).model
    return f'/api/v{options["version"]}/{_type}-list/history/'


def _create_few_models(factory):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()
    return last_obj


def _create_history_permission(user, model):
    content_type = ContentType.objects.get_for_model(model.history.model)
    permission = Permission.objects.get(
        content_type=content_type,
        codename__startswith='view_')
    user.user_permissions.add(permission)


def test_api_history_access_denied(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    res = api_client.get(url)

    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.data == {
        'code': 'permission_denied', 'message': 'Access denied'}


def test_api_history(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    _create_history_permission(api_client.user, model)
    res = api_client.get(url)

    assert res.status_code == status.HTTP_200_OK
    assert res.data['count'] == BATCH_MODELS + 1


def test_api_history_filter_by_uid(api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)
    _type = ContentType.objects.get_for_model(model).model

    _create_history_permission(api_client.user, model)
    res = api_client.get(f'{url}?_uid={last_obj.uid}')

    assert res.status_code == status.HTTP_200_OK
    count = res.data['count']
    first_result = res.data['results'][0]
    assert count == 1
    assert first_result['_uid'] == last_obj.uid
    assert first_result['_type'] == 'historical' + _type
    assert first_result['history_change_reason'] is None
    assert first_result['history_type'] == "+"


def test_api_history_create_and_change(api_client, api_model):  # noqa: invalid-name (pylint bug)
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)

    _create_history_permission(api_client.user, model)
    last_obj.save()
    res = api_client.get(f'{url}?_uid={last_obj.uid}')

    assert res.status_code == status.HTTP_200_OK
    assert res.data['count'] == 2
    first_result = res.data['results'][0]
    assert first_result['_uid'] == last_obj.uid
    assert first_result['history_change_reason'] is None
    assert first_result['history_type'] == "~"
    second_result = res.data['results'][1]
    assert second_result['_uid'] == last_obj.uid
    assert second_result['history_change_reason'] is None
    assert second_result['history_type'] == "+"
