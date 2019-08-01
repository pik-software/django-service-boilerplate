from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status

from core.tests.utils import add_user_permissions
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {'version': 1, 'queries': BATCH_MODELS}),
    (Comment, CommentFactory, {'version': 1, 'queries': BATCH_MODELS}),
])
def api_model(request):
    return request.param


def _url(model, options, obj=None):
    _type = ContentType.objects.get_for_model(model).model
    if obj:
        return f'/api/v{options["version"]}/{_type}-list/{obj.uid}/'
    return f'/api/v{options["version"]}/{_type}-list/'


def _create_few_models(factory):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()
    return last_obj


def test_api_unauthorized_list(anon_api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    res = anon_api_client.get(url)

    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_unauthorized_retrieve(anon_api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options, last_obj)

    res = anon_api_client.get(url)

    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_list(api_user, api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)
    _type = ContentType.objects.get_for_model(model).model

    add_user_permissions(api_user, model, 'view')
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


def test_api_retrieve(api_user, api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options, last_obj)
    _type = ContentType.objects.get_for_model(model).model

    add_user_permissions(api_user, model, 'view')
    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert res.data['_uid'] == last_obj.uid
    assert res.data['_type'] == _type


def test_api_list_num_queries(
        api_user, api_client, api_model,
        assert_num_queries_lte
):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)
    add_user_permissions(api_user, model, 'view')

    with assert_num_queries_lte(options["queries"]):
        res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) >= BATCH_MODELS
