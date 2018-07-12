# pylint: disable=protected-access
# pylint: disable=invalid-name
# pylint: disable=unused-variable
import json
from pprint import pprint

import pytest
from celery import exceptions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from eventsourcing.models import Subscription
from eventsourcing.replicator.serializer import _serialize
from eventsourcing.replicator.registry import _to_hist_obj
from eventsourcing.replicator.replicator import _get_subscription_statuses
from eventsourcing.replicator.serializer import _process_fake_request
from eventsourcing.replicator.tasks import _replicate_to_webhook_subscribers
from eventsourcing.replicator.tasks import _process_webhook_subscription
from eventsourcing.utils import HistoryObject
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
    return f'/api/v{options["version"]}/subscriptions/'


def _pack_history_instance(instance):
    return _to_hist_obj(instance).pack()


def _unpack_history_instance(packed_instance):
    return HistoryObject.unpack(*packed_instance).instance


def _create_few_models(factory):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()
    return last_obj


def _create_history_permission(user, model):
    model = model.history.model
    opts = model._meta  # noqa: pylint=protected-access
    content_type = ContentType.objects.get_for_model(model)
    permission = Permission.objects.get(
        content_type=content_type,
        codename=f'view_{opts.model_name}')
    user.user_permissions.add(permission)
    assert user.has_perm(
        f'{content_type.app_label}.view_{opts.model_name}')


def _create_subscription(model, options):
    user = create_user()
    _create_history_permission(user, model)
    _type = ContentType.objects.get_for_model(model).model
    return Subscription.objects.create(**{
        'events': [_type],
        'type': 1,
        'name': get_random_string(),
        'settings': {
            'api_version': options['version'],
            'webhook_url': 'http://localhost/'},
        'user': user,
    })


def _assert_api_res(res, code, result):
    data = res.json()
    pprint(data)
    assert res.status_code == code
    assert data == result


def test_api_create_subscription_access_denied(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    res = api_client.post(url, {
        "name": "test", "type": 1,
        "settings": {"webhook_url": "http://localhost/"},
        "events": [f"{model._meta.model_name}"],
    })

    _assert_api_res(res, status.HTTP_400_BAD_REQUEST, {
        'code': 'invalid',
        'detail': {'events': [
            {'code': 'no_event_permission',
             'message': 'no event permission'}
        ]},
        'message': 'Invalid input.'})


def test_api_create_subscription_without_type(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options)

    _create_history_permission(api_client.user, model)

    res = api_client.post(url, {
        'events': [f"{model._meta.model_name}"],
        'name': 'test', 'settings': {
            'webhook_url': 'http://localhost/',
        },
    })
    _assert_api_res(res, status.HTTP_400_BAD_REQUEST, {
        'code': 'invalid',
        'detail': {
            'type': [{'code': 'required',
                      'message': 'Это поле обязательно.'}]},
        'message': 'Invalid input.'})


def test_api_create_subscription_with_wrong_type(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options)

    _create_history_permission(api_client.user, model)

    res = api_client.post(url, {
        'events': [f"{model._meta.model_name}"],
        'name': 'test', 'type': 22, 'settings': {
            'webhook_url': 'http://localhost/',
        },
    })
    _assert_api_res(res, status.HTTP_400_BAD_REQUEST, {
        'code': 'invalid',
        'detail': {
            'type': [{'code': 'invalid_choice',
                      'message': '"22" не является корректным значением.'}]},
        'message': 'Invalid input.'})


def test_api_create_subscription_with_empty_events(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options)

    _create_history_permission(api_client.user, model)

    res = api_client.post(url, {
        'events': [],
        'name': 'test', 'type': 1, 'settings': {
            'webhook_url': 'http://localhost/',
        },
    })
    _assert_api_res(res, status.HTTP_400_BAD_REQUEST, {
        'code': 'invalid',
        'detail': {'events': [
            {'code': 'no_events', 'message': 'no events'}
        ]},
        'message': 'Invalid input.'})


def test_api_create_subscription(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options)
    _type = ContentType.objects.get_for_model(model).model

    _create_history_permission(api_client.user, model)

    res = api_client.post(url, {
        'events': [f"{model._meta.model_name}"],
        'name': 'test', 'type': 1, 'settings': {
            'webhook_url': 'http://localhost/',
        },
    })

    obj = Subscription.objects.last()

    _assert_api_res(res, status.HTTP_201_CREATED, {
        '_uid': str(obj.uid),
        '_type': 'subscription',
        'events': [_type],
        'type': 1,
        'name': 'test',
        'settings': {
            'api_version': options['version'],
            'webhook_url': 'http://localhost/'},
    })


def test_api_subscription_status_error_403(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options) + 'status/'
    _type = ContentType.objects.get_for_model(model).model

    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert res.json()[_type] == 'ERROR: serialize api status = 403'


def test_api_subscription_status_ok(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options) + 'status/'
    _type = ContentType.objects.get_for_model(model).model
    _create_history_permission(api_client.user, model)

    res = api_client.get(url)
    assert res.status_code == status.HTTP_200_OK
    assert res.json()[_type] == 'OK'


def test_replicate_call_on_create_update_delete(api_model, mocker):
    model, factory, options = api_model
    _create_subscription(model, options)
    model_type = ContentType.objects.get_for_model(model).model

    call_list = []

    def mock_replicate(hist_obj: HistoryObject, subscription=None):
        if model_type == hist_obj.instance_type:
            call_list.append([hist_obj.history_type, hist_obj.instance_uid])

    repl = mocker.patch.object(HistoryObject, 'replicate', autospec=True)
    repl.side_effect = mock_replicate

    # create
    obj = factory.create()
    obj_pk = str(obj.uid)

    # change event
    obj.version += 10
    obj.save()

    # delete event
    obj.delete()

    assert call_list == [['+', obj_pk], ['~', obj_pk], ['-', obj_pk]]


def test_serializer_process_fake_request(api_model):
    model, factory, options = api_model
    _type = ContentType.objects.get_for_model(model).model
    obj = _create_few_models(factory)
    hist_obj = obj.history.first()
    user = create_user()
    history_url = f'/api/v{options["version"]}/{_type}-list/history/'

    _create_history_permission(user, model)
    code, content = _process_fake_request(
        user, 'get', history_url, data={'history_id': hist_obj.history_id})

    print(content)
    assert code == 200

    content_json = json.loads(content)
    assert content_json['count'] == 1
    assert content_json['results'][0]["history_type"] == '+'
    assert content_json['results'][0]["history_id"] == hist_obj.history_id
    assert content_json['results'][0]["_uid"] == str(hist_obj.uid)
    assert content_json['results'][0]["_type"] == _type
    assert content_json['results'][0]['_version'] == obj.version


def test_serializer_serialize(api_model):
    model, factory, options = api_model
    _type = ContentType.objects.get_for_model(model).model
    obj = _create_few_models(factory)
    hist_obj = _to_hist_obj(obj.history.first())
    subscribe = _create_subscription(model, options)
    content = _serialize(subscribe.user, subscribe.settings, hist_obj)

    assert isinstance(content, str)
    content_json = json.loads(content)
    assert content_json['count'] == 1
    assert content_json['results'][0]["history_type"] == '+'
    assert content_json['results'][0]["history_id"] == hist_obj.history_id
    assert content_json['results'][0]["_uid"] == hist_obj._uid
    assert content_json['results'][0]["_type"] == _type
    assert content_json['results'][0]['_version'] == obj.version


def test_task_replicate_to_webhook_subscribers(
        api_model, mocker, celery_worker):
    model, factory, options = api_model
    subscribe = _create_subscription(model, options)
    process_webhook = mocker.patch(
        'eventsourcing.replicator.tasks._process_webhook_subscription')
    mocker.patch.object(HistoryObject, 'deliver', autospec=True)

    # create event
    obj = factory.create()
    history = obj.history.all()
    hist = history.first()
    packed_history = _pack_history_instance(hist)

    r = _replicate_to_webhook_subscribers.delay(packed_history)
    r.get(timeout=10)
    process_webhook.delay.assert_called_with(
        subscribe.pk, list(packed_history))

    # change event
    obj.version += 10
    obj.save()
    hist = history.first()
    packed_history = _pack_history_instance(hist)

    r = _replicate_to_webhook_subscribers.delay(packed_history)
    r.get(timeout=10)
    process_webhook.delay.assert_called_with(
        subscribe.pk, list(packed_history))

    # delete event
    obj.delete()
    hist = history.first()
    packed_history = _pack_history_instance(hist)

    r = _replicate_to_webhook_subscribers.delay(packed_history)
    r.get(timeout=10)
    process_webhook.delay.assert_called_with(
        subscribe.pk, list(packed_history))


def test_process_webhook_ok(api_model, mocker, celery_worker):
    model, factory, options = api_model
    obj = _create_few_models(factory)
    history = obj.history.all()
    hist_obj = _to_hist_obj(history.first())
    packed_history = hist_obj.pack()
    subscription = _create_subscription(model, options)
    result = get_random_string()

    step1_serialize = mocker.patch.object(
        HistoryObject, 'serialize', autospec=True)
    step1_serialize.return_value = result
    step2_deliver = mocker.patch.object(
        HistoryObject, 'deliver', autospec=True)

    r = _process_webhook_subscription.delay(subscription.pk, packed_history)

    assert r.get(timeout=10) == 'ok'
    step1_serialize.assert_called_once_with(hist_obj, subscription)
    step2_deliver.assert_called_once_with(hist_obj, subscription, result)


def test_process_webhook_retry(api_model, celery_worker):
    model, factory, options = api_model
    obj = factory.create()
    hist_obj = obj.history.first()
    subscribe = _create_subscription(model, options)
    packed_history = _pack_history_instance(hist_obj)

    r = _process_webhook_subscription.delay(
        subscribe.pk, packed_history)
    with pytest.raises(exceptions.TimeoutError):
        r.get(timeout=0.1)
    r.revoke()


def test_check_model_replicating(api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    subs = _create_subscription(model, options)
    statuses = _get_subscription_statuses(subs.user, subs.settings)
    _type = subs.events[0]
    assert statuses[_type] == 'OK'
