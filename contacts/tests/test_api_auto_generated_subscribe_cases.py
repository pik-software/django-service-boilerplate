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
from eventsourcing.replicator.tasks import _do_async_fake_request, \
    _replicate_to_webhook_subscribers, \
    _replicate_history_process_webhook_subscriber
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


def _get_history_content(model, options, user, hist_obj):
    _type = ContentType.objects.get_for_model(model).model
    history_url = f'/api/v{options["version"]}/{_type}-list/history/'
    status, content = _do_async_fake_request(
        user.pk, 'get', history_url, data={'history_id': hist_obj.history_id})
    assert status == 200
    return content


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


def test_api_subscribe_without_type(api_client, api_model):
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


def test_api_subscribe_with_wrong_type(api_client, api_model):
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


def test_api_subscribe_with_empty_events(api_client, api_model):
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


def test_api_subscribe(api_client, api_model):
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


def test_subscription_replicate_to_webhook_subscribers(api_model, mocker):
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
        hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk,
    )

    # change event
    obj.version += 10
    obj.save()
    hist_obj = history.first()

    _assert_history_object(hist_obj, _type, '~', _uid)
    task.delay.assert_called_with(
        hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk,
    )

    # delete event
    obj.delete()
    hist_obj = history.first()

    _assert_history_object(hist_obj, _type, '-', _uid)
    task.delay.assert_called_with(
        hist_obj._meta.app_label, hist_obj._meta.model_name, hist_obj.pk,
    )


def test_subscription_replicate(api_model, mocker):
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
    code, content = _do_async_fake_request(
        user.pk, 'get', history_url, data={'history_id': hist_obj.history_id})

    print(content)
    assert code == 200

    content_json = json.loads(content)
    assert content_json['count'] == 1
    assert content_json['results'][0]["history_type"] == '+'
    assert content_json['results'][0]["history_id"] == hist_obj.history_id
    assert content_json['results'][0]["_uid"] == str(hist_obj.uid)
    assert content_json['results'][0]["_type"] == 'historical' + _type


def test_replicate_history_call_process_webhook(
        api_model, mocker, celery_session_worker):
    model, factory, options = api_model
    subscribe = _create_subscription(model, options)
    process_webhook = mocker.patch(
        'eventsourcing.replicator.tasks.'
        '_replicate_history_process_webhook_subscriber')

    # create event
    obj = factory.create()
    history = obj.history.all()
    hist1 = history.first()
    app_label, model_name = hist1._meta.app_label, hist1._meta.model_name

    r = _replicate_to_webhook_subscribers.delay(
        app_label, model_name, hist1.pk)
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist1.pk),
    ]

    # change event
    obj.version += 10
    obj.save()
    hist2 = history.first()

    r = _replicate_to_webhook_subscribers.delay(
        app_label, model_name, hist2.pk)
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist2.pk),
        call(subscribe.pk, app_label, model_name, hist2.pk),
    ]

    # delete event
    obj.delete()
    hist3 = history.first()

    r = _replicate_to_webhook_subscribers.delay(
        app_label, model_name, hist3.pk)
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist2.pk),
        call(subscribe.pk, app_label, model_name, hist2.pk),
        call(subscribe.pk, app_label, model_name, hist3.pk),
        call(subscribe.pk, app_label, model_name, hist3.pk),
    ]


def test_process_webhook(api_model, mocker, celery_session_worker):
    model, factory, options = api_model
    obj = _create_few_models(factory)
    history = obj.history.all()
    hist1 = history.first()

    subscribe = _create_subscription(model, options)
    transfer = mocker.patch(
        'eventsourcing.replicator.tasks._transfer_webhook_data')
    transfer.return_value = 200, ''
    hist1_content = _get_history_content(model, options, subscribe.user, hist1)
    app_label, model_name = hist1._meta.app_label, hist1._meta.model_name

    r = _replicate_history_process_webhook_subscriber.delay(
        subscribe.pk, app_label, model_name, hist1.pk)

    assert r.get(timeout=10) == 'ok'
    print(transfer.call_args_list)
    assert transfer.call_args_list == [
        call('http://localhost/', auth=None, cookies=None, data=hist1_content,
             headers={'content-type': 'application/json'}),
    ]


def test_process_webhook_retry(api_model, celery_session_worker):
    model, factory, options = api_model
    obj = factory.create()
    hist_obj = obj.history.first()
    app_label, model_name = hist_obj._meta.app_label, hist_obj._meta.model_name
    subscribe = _create_subscription(model, options)

    r = _replicate_history_process_webhook_subscriber.delay(
        subscribe.pk, app_label, model_name, hist_obj.pk)
    with pytest.raises(exceptions.TimeoutError):
        r.get(timeout=0.1)
