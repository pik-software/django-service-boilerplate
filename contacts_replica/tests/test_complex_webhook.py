from time import sleep

import pytest
from django.contrib.auth.models import Permission, AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from contacts.models import Contact, Comment
from contacts.tests.factories import ContactFactory, CommentFactory
from contacts_replica.models import ContactReplica, CommentReplica
from eventsourcing.models import Subscription
from core.tasks.fixtures import create_user


@pytest.fixture(params=[
    (Contact, [], ContactFactory, ContactReplica, {'version': 1}),
    (Comment, [Contact], CommentFactory, CommentReplica, {'version': 1}),
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


def test_webhook_replication(celery_session_worker, base_url,
                             api_client, api_model):
    model, dep_models, factory, replica_model, options = api_model
    for dep_model in dep_models:
        _create_subscribe(
            api_client.user, api_client.password, dep_model, options, base_url)
    _create_subscribe(
        api_client.user, api_client.password, model, options, base_url)

    x = factory.create()
    sleep(1)  # TODO: replace to celery magic ... (wait until the action)
    y = replica_model.objects.get(uid=x.uid)
    assert x.version == y.version
    assert x.uid == y.uid
