from django.contrib.contenttypes.models import ContentType
import pytest
from freezegun import freeze_time
from rest_framework import status

from core.tests.utils import add_permissions
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {'version': 1}),
    (Comment, CommentFactory, {'version': 1}),
])
def api_model(request):
    return request.param


def _url(model, options):
    _type = ContentType.objects.get_for_model(model).model
    return f'/api/v{options["version"]}/{_type}-list/history/'


def _create_few_models(factory):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()
    return last_obj


def _assert_history_object(hist_obj, type_, event_, uid_):
    _type = hist_obj.history_object._meta.model_name  # noqa
    _hist_type = hist_obj._meta.model_name  # noqa
    _event = hist_obj.history_type
    _uid = hist_obj.history_object.uid
    assert _type == type_
    assert _event == event_
    assert _uid == uid_
    assert _hist_type == 'historical' + type_


def test_api_history_access_denied(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    res = api_client.get(url)

    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.data == {
        'code': 'permission_denied',
        'message': 'У вас нет прав для выполнения этой операции.'}


def test_api_history(api_user, api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    add_permissions(api_user, model.history.model, 'view')
    res = api_client.get(url)

    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == BATCH_MODELS + 1


def test_api_history_filter_by_uid(api_user, api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)
    _type = ContentType.objects.get_for_model(model).model

    add_permissions(api_user, model.history.model, 'view')
    res = api_client.get(f'{url}?_uid={last_obj.uid}')

    assert res.status_code == status.HTTP_200_OK
    first_result = res.data['results'][0]
    assert len(res.data['results']) == 1
    assert first_result['_uid'] == last_obj.uid
    assert first_result['_type'] == 'historical' + _type
    assert first_result['_version'] >= 1
    assert first_result['history_change_reason'] is None
    assert first_result['history_type'] == "+"


def test_api_history_filter_by_date(api_user, api_client, api_model):
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)

    add_permissions(api_user, model.history.model, 'view')
    last_obj.save()
    history = last_obj.history.last()
    history.history_date = '2000-01-01 00:00:00'
    history.save()

    res = api_client.get(f'{url}?history_date__lt=2000-01-01T00:00:01')
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == 1

    res = api_client.get(f'{url}?history_date__gt=2000-01-01T00:00:01')
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == BATCH_MODELS + 1

    res = api_client.get(f'{url}?history_date__lt=2000-01-01 00:00:01')
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == 1

    res = api_client.get(f'{url}?history_date__gt=2000-01-01 00:00:01')
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == BATCH_MODELS + 1


def test_api_history_create_and_change(api_user, api_client, api_model):  # noqa: invalid-name (pylint bug)
    model, factory, options = api_model
    last_obj = _create_few_models(factory)
    url = _url(model, options)

    add_permissions(api_user, model.history.model, 'view')

    last_obj.save()
    res = api_client.get(f'{url}?_uid={last_obj.uid}')

    assert res.status_code == status.HTTP_200_OK
    assert len(res.data['results']) == 2
    first_result = res.data['results'][0]
    assert first_result['_uid'] == last_obj.uid
    assert first_result['history_change_reason'] is None

    assert first_result['history_type'] == "+"
    second_result = res.data['results'][1]
    assert second_result['_uid'] == last_obj.uid
    assert second_result['history_change_reason'] is None
    assert second_result['history_type'] == "~"


def test_history_events(api_model):
    model, factory, _ = api_model
    _type = ContentType.objects.get_for_model(model).model

    # create event
    obj = factory.create()

    history = obj.history.all()
    _uid = obj.uid

    hist_obj = history.first()
    _assert_history_object(hist_obj, _type, '+', _uid)

    # change event
    obj.version += 10
    obj.save()

    hist_obj = history.first()
    _assert_history_object(hist_obj, _type, '~', _uid)

    # delete event
    obj.delete()

    hist_obj = history.first()
    _assert_history_object(hist_obj, _type, '-', _uid)
