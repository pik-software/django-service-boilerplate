import json
from pprint import pprint
from unittest.mock import call

import pytest
from celery import exceptions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

import eventsourcing.replicator.registry
from core.tasks.fixtures import create_user
from eventsourcing.models import Subscription
from eventsourcing.replicator import serialize
from eventsourcing.replicator.serializer import _process_fake_request
from eventsourcing.replicator.tasks import _replicate_to_webhook_subscribers, \
    _process_webhook_subscription
from eventsourcing.utils import _pack_history_instance
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


def _assert_history_object(hist_obj, type_, event_, uid_):
    _type = hist_obj.history_object._meta.model_name  # noqa
    _event = hist_obj.history_type
    _uid = hist_obj.history_object.uid
    assert _type == type_
    assert _event == event_
    assert _uid == uid_


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


def test_replicate_to_webhook_subscribers(api_model, mocker):
    model, factory, options = api_model
    _create_subscription(model, options)
    _type = ContentType.objects.get_for_model(model).model
    task = mocker.patch(
        'eventsourcing.replicator.registry._replicate_to_webhook_subscribers')

    obj = factory.create()
    history = obj.history.all()
    _uid = obj.uid

    hist_obj = history.first()

    # create event
    _assert_history_object(hist_obj, _type, '+', _uid)
    task.delay.assert_called_once_with(
        (hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk),
    )

    # change event
    obj.version += 10
    obj.save()
    hist_obj = history.first()

    _assert_history_object(hist_obj, _type, '~', _uid)
    task.delay.assert_called_with(
        (hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk),
    )

    # delete event
    obj.delete()
    hist_obj = history.first()

    _assert_history_object(hist_obj, _type, '-', _uid)
    task.delay.assert_called_with(
        (hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk),
    )


def test_replicate(api_model, mocker):
    model, factory, options = api_model
    _create_subscription(model, options)

    repl = mocker.patch.object(eventsourcing.replicator, 'replicate')

    obj = factory.create()
    history = obj.history.all()

    hist_obj = history.first()
    repl.assert_called_once_with(hist_obj)

    # change event
    obj.version += 10
    obj.save()
    hist_obj = history.first()
    repl.assert_called_with(hist_obj)

    # delete event
    obj.delete()
    hist_obj = history.first()
    repl.assert_called_with(hist_obj)


def test_do_async_fake_request(api_model):
    model, factory, options = api_model
    _type = ContentType.objects.get_for_model(model).model
    obj = _create_few_models(factory)
    hist_obj = obj.history.first()
    user = create_user()
    history_url = f'/api/v{options["version"]}/{_type}-list/history/'

    _create_history_permission(user, model)
    code, content = _process_fake_request(
        user.pk, 'get', history_url, data={'history_id': hist_obj.history_id})

    print(content)
    assert code == 200

    content_json = json.loads(content)
    assert content_json['count'] == 1
    assert content_json['results'][0]["history_type"] == '+'
    assert content_json['results'][0]["history_id"] == hist_obj.history_id
    assert content_json['results'][0]["_uid"] == str(hist_obj.uid)
    assert content_json['results'][0]["_type"] == _type
    assert content_json['results'][0]['_version'] == obj.version


def test_serialize(api_model):
    model, factory, options = api_model
    _type = ContentType.objects.get_for_model(model).model
    obj = _create_few_models(factory)
    hist_obj = obj.history.first()
    subscribe = _create_subscription(model, options)
    content = serialize(subscribe.user, subscribe.settings, hist_obj)

    assert isinstance(content, str)
    content_json = json.loads(content)
    assert content_json['count'] == 1
    assert content_json['results'][0]["history_type"] == '+'
    assert content_json['results'][0]["history_id"] == hist_obj.history_id
    assert content_json['results'][0]["_uid"] == str(hist_obj.uid)
    assert content_json['results'][0]["_type"] == _type
    assert content_json['results'][0]['_version'] == obj.version


def test_replicate_history_call_process_webhook(
        api_model, mocker, celery_session_worker):
    model, factory, options = api_model
    subscribe = _create_subscription(model, options)
    process_webhook = mocker.patch(
        'eventsourcing.replicator.tasks.'
        '_process_webhook_subscription')

    # create event
    obj = factory.create()
    history = obj.history.all()
    hist1 = history.first()
    app_label, model_name = hist1._meta.app_label, hist1._meta.model_name

    r = _replicate_to_webhook_subscribers.delay(
        (app_label, model_name, hist1.pk))
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
    ]

    # change event
    obj.version += 10
    obj.save()
    hist2 = history.first()

    r = _replicate_to_webhook_subscribers.delay(
        (app_label, model_name, hist2.pk))
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
        call(subscribe.pk, [app_label, model_name, hist2.pk]),
        call(subscribe.pk, [app_label, model_name, hist2.pk]),
    ]

    # delete event
    obj.delete()
    hist3 = history.first()

    r = _replicate_to_webhook_subscribers.delay(
        (app_label, model_name, hist3.pk))
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
        call(subscribe.pk, [app_label, model_name, hist1.pk]),
        call(subscribe.pk, [app_label, model_name, hist2.pk]),
        call(subscribe.pk, [app_label, model_name, hist2.pk]),
        call(subscribe.pk, [app_label, model_name, hist3.pk]),
        call(subscribe.pk, [app_label, model_name, hist3.pk]),
    ]


def test_process_webhook_ok(api_model, mocker, celery_session_worker):
    model, factory, options = api_model
    obj = _create_few_models(factory)
    history = obj.history.all()
    hist1 = history.first()
    subscription = _create_subscription(model, options)
    packed_history = _pack_history_instance(hist1)
    result = get_random_string()

    step1_serialize = mocker.patch(
        'eventsourcing.replicator.tasks.serialize')
    step1_serialize.return_value = result
    step2_run_webhook_request = mocker.patch(
        'eventsourcing.replicator.tasks._run_request_to_webhook')
    step2_run_webhook_request.return_value = 200, ''

    r = _process_webhook_subscription.delay(subscription.pk, packed_history)

    assert r.get(timeout=10) == 'ok'
    step1_serialize.assert_called_once_with(
        subscription.user, subscription.settings, hist1)
    step2_run_webhook_request.assert_called_once_with(
        subscription.user, subscription.settings, result)


def test_process_webhook_retry(api_model, celery_session_worker):
    model, factory, options = api_model
    obj = factory.create()
    hist_obj = obj.history.first()
    subscribe = _create_subscription(model, options)
    packed_history = _pack_history_instance(hist_obj)

    r = _process_webhook_subscription.delay(
        subscribe.pk, packed_history)
    with pytest.raises(exceptions.TimeoutError):
        r.get(timeout=0.1)
