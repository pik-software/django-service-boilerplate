import json
from unittest.mock import call

import celery
from celery.exceptions import Retry
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import pytest
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

import replication.tasks
from core.tasks.fixtures import create_user
from replication.models import Subscribe
from replication.tasks import _do_async_fake_request, replicate_history, \
    _replicate_history_process_webhook_subscriber, _transfer_webhook_data
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {'version': 1}),
    # (Comment, CommentFactory, {'version': 1}),
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
    return f'/api/v{options["version"]}/{_type}-list/subscribe/'


def _create_few_models(factory):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create()
    return last_obj


def _create_subscribe_permission(user, model):
    model_type_name = ContentType.objects.get_for_model(model).model
    # permission = Permission.objects.get(
    #     codename=f'can_post_api_{model_type_name}_subscribe')
    # user.user_permissions.add(permission)


def _create_history_permission(user, model):
    opts = model._meta  # noqa: pylint=protected-access
    content_type = ContentType.objects.get_for_model(model)
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename=f'view_historical{opts.model_name}')
    user.user_permissions.add(permission)


def _create_subscribe(model, options):
    user = create_user()
    _create_history_permission(user, model)
    _type = ContentType.objects.get_for_model(model).model
    return Subscribe.objects.create(**{
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
    _uid = hist_obj.history_object.pk
    assert _type == type_
    assert _event == event_
    assert _uid == uid_


def _get_history_content(model, options, user, hist_obj):
    _type = ContentType.objects.get_for_model(model).model
    history_url = f'/api/v{options["version"]}/{_type}-list/history/'
    status, content = _do_async_fake_request(
        user.pk, 'get', history_url, data={'history_id': hist_obj.history_id})
    assert status == 200
    return content


def test_api_subscribe_access_denied(api_client, api_model):
    model, factory, options = api_model
    _create_few_models(factory)
    url = _url(model, options)

    res = api_client.post(url, {"name": "test"})

    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.data == {
        'code': 'permission_denied', 'message': 'Access denied'}


def test_api_subscribe(api_client, api_model):
    model, factory, options = api_model
    url = _url(model, options)
    _type = ContentType.objects.get_for_model(model).model

    _create_subscribe_permission(api_client.user, model)
    res = api_client.post(url, {
        'name': 'test', 'type': 1, 'settings': {
            'webhook_url': 'http://localhost/',
        },
    })

    obj = Subscribe.objects.last()

    print(res.data)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        '_uid': obj.uid,
        '_type': 'subscribe',
        'events': [_type],
        'type': 1,
        'name': 'test',
        'settings': {
            'api_version': options['version'],
            'webhook_url': 'http://localhost/'},
    }


def test_api_subscribe_events(api_model, mocker):
    model, factory, options = api_model
    _create_subscribe(model, options)
    _type = ContentType.objects.get_for_model(model).model
    task = mocker.patch('replication.tasks.replicate_history')

    obj = factory.create()
    history = obj.history.all()
    _uid = obj.pk

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


def test_do_async_fake_request(api_model):
    model, factory, options = api_model
    user = create_user()
    _create_history_permission(user, model)
    _type = ContentType.objects.get_for_model(model).model
    obj = _create_few_models(factory)
    hist_obj = obj.history.first()
    history_url = f'/api/v{options["version"]}/{_type}-list/history/'

    code, content = _do_async_fake_request(
        user.pk, 'get', history_url, data={'history_id': hist_obj.history_id})

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
    subscribe = _create_subscribe(model, options)
    process_webhook = mocker.patch(
        'replication.tasks._replicate_history_process_webhook_subscriber')

    # create event
    obj = factory.create()
    history = obj.history.all()
    hist1 = history.first()
    app_label, model_name = hist1._meta.app_label, hist1._meta.model_name

    r = replicate_history.delay(app_label, model_name, hist1.pk)
    r.get(timeout=10)
    assert process_webhook.delay.call_args_list == [
        call(subscribe.pk, app_label, model_name, hist1.pk),
        call(subscribe.pk, app_label, model_name, hist1.pk),
    ]

    # change event
    obj.version += 10
    obj.save()
    hist2 = history.first()

    r = replicate_history.delay(app_label, model_name, hist2.pk)
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

    r = replicate_history.delay(app_label, model_name, hist3.pk)
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
    subscribe = _create_subscribe(model, options)
    process_webhook = _replicate_history_process_webhook_subscriber
    transfer = mocker.patch('replication.tasks._transfer_webhook_data')

    # create event
    obj = _create_few_models(factory)
    history = obj.history.all()
    hist1 = history.first()
    hist1_content = _get_history_content(model, options, subscribe.user, hist1)
    app_label, model_name = hist1._meta.app_label, hist1._meta.model_name

    r = process_webhook.delay(subscribe.pk, app_label, model_name, hist1.pk)
    assert r.get(timeout=10) == 'ok'
    assert transfer.call_args_list == [
        call('http://localhost/', hist1_content),
        call('http://localhost/', hist1_content),
    ]


def test_process_webhook_retry(api_model, celery_session_worker):
    model, factory, options = api_model
    subscribe = _create_subscribe(model, options)
    process_webhook = _replicate_history_process_webhook_subscriber

    obj = factory.create()
    hist_obj = obj.history.first()
    app_label, model_name = hist_obj._meta.app_label, hist_obj._meta.model_name
    r = process_webhook.delay(subscribe.pk, app_label, model_name, hist_obj.pk)
    with pytest.raises(Retry):
        r.get(timeout=12)
