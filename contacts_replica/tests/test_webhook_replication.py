# pylint: disable=invalid-name
from time import sleep, time

import pytest
from django.contrib.auth.models import Permission, AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from eventsourcing.models import Subscription
from eventsourcing import tasks
from contacts.models import Contact, Comment
from contacts.tests.factories import ContactFactory, CommentFactory
from contacts_replica.models import ContactReplica, CommentReplica


UNICHRS = 'abcdefабвгдеàHЯ⾀HÐ¯â¾€ЯЯ×�¼½¾¿™Ž'
assert tasks


@pytest.fixture(params=[
    (Contact, [], ContactFactory, ContactReplica, {
        'version': 1, 'field': 'name'}),
    (Comment, [Contact], CommentFactory, CommentReplica, {
        'version': 1, 'field': 'message'}),
])
def api_model(request):
    return request.param


@pytest.fixture
def api_client():
    password = get_random_string()
    user = create_user(password=password)
    client = APIClient()
    client.force_login(user)
    client.user = user
    client.password = password
    return client


def _create_history_permission(user, model):
    model = model.history.model
    opts = model._meta  # noqa: pylint=protected-access
    content_type = ContentType.objects.get_for_model(model)
    permission = Permission.objects.get(
        content_type=content_type,
        codename=f'view_{opts.model_name}')
    user.user_permissions.add(permission)


def _create_subscribe(user: AbstractUser, password, model, options, base_url):
    _create_history_permission(user, model)
    _type = ContentType.objects.get_for_model(model).model
    return Subscription.objects.create(**{
        'events': [_type],
        'type': 1,
        'name': get_random_string(),
        'settings': {
            'api_version': options['version'],
            'webhook_url': f'{base_url}/api/v1/webhook/',
            'webhook_auth': [user.get_username(), password],
        },
        'user': user,
    })


def _create_deep_subscribe(
        user: AbstractUser, password, model, dep_models, options, base_url,
):
    for dep_model in dep_models:
        _create_subscribe(
            user, password, dep_model, options, base_url)
    _create_subscribe(
        user, password, model, options, base_url)


def _wait_query(model, kwargs, condition=lambda qs: qs.exists(), timeout=9.0):
    time1 = time()
    while time() - time1 < timeout:
        q_set = model.objects.filter(**kwargs)
        if condition(q_set):
            return q_set
        sleep(0.1)
    raise AssertionError('_wait_object() timeout')


def test_webhook_create_event(celery_worker, base_url, api_client, api_model):
    model, dep_models, factory, replica_model, options = api_model
    _create_deep_subscribe(
        api_client.user, api_client.password, model, dep_models, options,
        base_url)

    obj = factory.create()

    replica_obj = _wait_query(replica_model, dict(uid=obj.uid)).last()
    assert obj.version == replica_obj.version
    assert obj.uid == replica_obj.uid


def test_webhook_update_event(
        celery_worker, base_url, api_client, api_model):
    model, dep_models, factory, replica_model, options = api_model
    _create_deep_subscribe(
        api_client.user, api_client.password, model, dep_models, options,
        base_url)
    val1, val2 = get_random_string(9, UNICHRS), get_random_string(13, UNICHRS)

    obj = factory.create(**{options['field']: val1})
    _wait_query(replica_model, {options['field']: val1, 'uid': obj.uid})

    setattr(obj, options['field'], val2)
    obj.save()
    _wait_query(replica_model, {options['field']: val2, 'uid': obj.uid})


def test_webhook_delete_event(celery_worker, base_url, api_client, api_model):
    model, dep_models, factory, replica_model, options = api_model
    _create_deep_subscribe(
        api_client.user, api_client.password, model, dep_models, options,
        base_url)

    obj = factory.create()
    _wait_query(replica_model, dict(uid=obj.uid))

    obj.delete()
    _wait_query(replica_model, dict(uid=obj.uid), lambda qs: not qs.exists())
