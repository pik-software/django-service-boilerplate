import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {'version': 1, 'queries': BATCH_MODELS}),
    (Comment, CommentFactory, {'version': 1, 'queries': BATCH_MODELS}),
])
def api_model(request):
    return request.param


@pytest.fixture
def api_client():
    user = create_user()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


def test_api_list(api_client, api_model):  # noqa: pylint=redefined-outer-name
    model, factory, options = api_model
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()

    _type = ContentType.objects.get_for_model(model).model

    url = f'/api/v{options["version"]}/{_type}-list/'
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert res.data['count'] > BATCH_MODELS
    assert res.data['pages'] >= 1
    assert res.data['page_size'] >= 20
    assert res.data['page'] == 1
    assert res.data['page_next'] is None or res.data['page_next'] == 2
    assert res.data['page_previous'] is None
    assert res.data['results'][0]['_uid'] == last_obj.uid
    assert res.data['results'][0]['_type'] == _type
    assert len(res.data['results']) > BATCH_MODELS


def test_api_retrieve(api_client, api_model):  # noqa: pylint=redefined-outer-name
    model, factory, options = api_model

    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()

    _type = ContentType.objects.get_for_model(model).model

    url = f'/api/v{options["version"]}/{_type}-list/{last_obj.uid}/'
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert res.data['_uid'] == last_obj.uid
    assert res.data['_type'] == _type


def test_api_list_num_queries(
        api_client, api_model,  # noqa: pylint=redefined-outer-name
        assert_num_queries_lte
):
    model, factory, options = api_model
    factory.create_batch(BATCH_MODELS)
    _type = ContentType.objects.get_for_model(model).model

    url = f'/api/v{options["version"]}/{_type}-list/'

    with assert_num_queries_lte(options["queries"]):
        res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) >= BATCH_MODELS
