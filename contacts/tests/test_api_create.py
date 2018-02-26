import django.test
import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from contacts.tests.factories import ContactFactory
from core.tests.fixtures import create_user


REQUIRED_FIELD_ERROR = {'message': 'Это поле обязательно.', 'code': 'required'}


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture
def logged_user_client(client: django.test.Client):
    user = create_user()
    client.force_login(user)
    client.user = user
    return client


def test_api_authorization(client):
    res = client.get('/api/v1/')
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_contact_create_without_request_user(client):
    data = {'name': get_random_string()}
    res = client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_contact_create(logged_user_client):
    data = {'name': get_random_string()}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_contact_create_bulk(logged_user_client):
    data = [{'name': get_random_string()}, {'name': get_random_string()}]
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2


def test_api_contact_create_without_name(logged_user_client):
    data = {'noname': get_random_string()}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'name': [REQUIRED_FIELD_ERROR]},
        'message': 'Invalid input.'}


def test_api_contact_create_with_extra_field(logged_user_client):
    data = {'name': get_random_string(), 'fooo': 'no'}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_comment_create_without_request_user(client):
    data = {'message': get_random_string()}
    res = client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_comment_create_without_user(logged_user_client):
    data = {'message': get_random_string()}
    res = logged_user_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'message': 'Invalid input.', 'code': 'invalid',
        'detail': {
            'contact': [REQUIRED_FIELD_ERROR],
        }
    }


def test_api_comment_create(logged_user_client):
    contact = ContactFactory.create()
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
        'name': get_random_string(),
    }

    data = {'message': get_random_string(), 'contact': payload}
    res = logged_user_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data == {
        '_uid': res.data['_uid'],
        '_type': 'comment',
        'user': logged_user_client.user.pk,
        'message': data['message'],
        'contact': {
            '_uid': contact.uid,
            '_type': 'contact',
            'name': contact.name,
            'phones': contact.phones,
            'emails': contact.emails,
            'order_index': contact.order_index,
        },
    }


def test_api_comment_create_simple(logged_user_client):
    contact = ContactFactory.create()
    data = {'message': get_random_string(), 'contact': contact.uid}
    res = logged_user_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data == {
        '_uid': res.data['_uid'],
        '_type': 'comment',
        'user': logged_user_client.user.pk,
        'message': data['message'],
        'contact': {
            '_uid': contact.uid,
            '_type': 'contact',
            'name': contact.name,
            'phones': contact.phones,
            'emails': contact.emails,
            'order_index': contact.order_index,
        },
    }


def test_api_comment_create_2_comments_for_one_contact(logged_user_client):
    contact = ContactFactory.create()
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
    }

    data = [
        {'message': get_random_string(), 'contact': payload},
        {'message': get_random_string(), 'contact': payload},]
    res = logged_user_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2
    assert contact.comments.all().count() == 2
