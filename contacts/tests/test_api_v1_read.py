from pprint import pprint

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


@pytest.fixture
def api_client():
    user = create_user()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


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


def _assert_api_object_list(res, result):
    data = res.json()['results']
    pprint(data)
    assert data == result


def _assert_api_object(res, result):
    data = res.json()
    pprint(data)
    assert data == result


def test_api_list_contact(api_client):  # noqa: pylint=invalid-name
    obj = ContactFactory.create()
    res = api_client.get('/api/v1/contact-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [
        {
            '_uid': str(obj.uid),
            '_type': 'contact',
            '_version': obj.version,
            'emails': obj.emails,
            'name': obj.name,
            'order_index': obj.order_index,
            'phones': obj.phones,
        }
    ])


def test_api_retrieve_contact(api_client):
    obj = ContactFactory.create()
    res = api_client.get(f'/api/v1/contact-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res, {
        '_uid': str(obj.uid),
        '_type': 'contact',
        '_version': obj.version,
        'emails': obj.emails,
        'name': obj.name,
        'order_index': obj.order_index,
        'phones': obj.phones,
    })


def test_api_contact_history(api_client):
    obj = ContactFactory.create()
    hist_obj = obj.history.last()
    _create_history_permission(api_client.user, Contact)
    res = api_client.get(f'/api/v1/contact-list/history/?_uid={obj.uid}')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [{
        '_uid': str(obj.uid),
        '_type': 'contact',
        '_version': obj.version,
        'emails': obj.emails,
        'name': obj.name,
        'order_index': obj.order_index,
        'phones': obj.phones,
        'history_change_reason': None,
        'history_date': hist_obj.history_date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'history_id': hist_obj.history_id,
        'history_type': '+',
        'history_user_id': None,
    }])


def test_api_list_comment(api_client):  # noqa: pylint=invalid-name
    obj = CommentFactory.create()
    res = api_client.get('/api/v1/comment-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [
        {
            '_uid': str(obj.uid),
            '_type': 'comment',
            '_version': obj.version,
            'contact': {
                '_uid': str(obj.contact.uid),
                '_type': 'contact',
                '_version': obj.contact.version,
                'emails': obj.contact.emails,
                'name': obj.contact.name,
                'order_index': obj.contact.order_index,
                'phones': obj.contact.phones,
            },
            'message': obj.message,
            'user': obj.user.pk,
        }
    ])


def test_api_retrieve_comment(api_client):
    obj = CommentFactory.create()
    res = api_client.get(f'/api/v1/comment-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res, {
        '_uid': str(obj.uid),
        '_type': 'comment',
        '_version': obj.version,
        'contact': {
            '_uid': str(obj.contact.uid),
            '_type': 'contact',
            '_version': obj.contact.version,
            'emails': obj.contact.emails,
            'name': obj.contact.name,
            'order_index': obj.contact.order_index,
            'phones': obj.contact.phones,
        },
        'message': obj.message,
        'user': obj.user.pk,
    })


def test_api_comment_history(api_client):
    obj = CommentFactory.create()
    hist_obj = obj.history.last()
    _create_history_permission(api_client.user, Comment)
    res = api_client.get(f'/api/v1/comment-list/history/?_uid={obj.uid}')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [{
        '_uid': str(obj.uid),
        '_type': 'comment',
        '_version': obj.version,
        'contact': {
            '_uid': str(obj.contact.uid),
            '_type': 'contact',
            '_version': obj.contact.version,
            'emails': obj.contact.emails,
            'name': obj.contact.name,
            'order_index': obj.contact.order_index,
            'phones': obj.contact.phones,
        },
        'message': obj.message,
        'user': obj.user.pk,
        'history_change_reason': None,
        'history_date': hist_obj.history_date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'history_id': hist_obj.history_id,
        'history_type': '+',
        'history_user_id': None,
    }])
