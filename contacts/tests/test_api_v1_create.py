from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from ..tests.factories import ContactFactory


REQUIRED_FIELD_ERROR = {'message': 'Это поле обязательно.', 'code': 'required'}


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


def test_api_unauthorized(client):
    res = client.get('/api/v1/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_contact_unauthorized(client):  # noqa: pylint=invalid-name
    data = {'name': get_random_string()}
    res = client.post('/api/v1/contact-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_contact_without_name(api_client):  # noqa: pylint=invalid-name
    data = {'noname': get_random_string()}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'name': [REQUIRED_FIELD_ERROR]},
        'message': 'Invalid input.'}


def test_api_create_contact_with_extra_field(api_client):  # noqa: pylint=invalid-name
    data = {'name': get_random_string(), 'fooo': 'no'}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_create_contact(api_client):
    data = {'name': get_random_string()}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_create_bulk_contact(api_client):
    data = [{'name': get_random_string()}, {'name': get_random_string()}]
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2


def test_api_create_comment_unauthorized(client):  # noqa: pylint=invalid-name
    data = {'message': get_random_string()}
    res = client.post('/api/v1/comment-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_comment_without_contact(api_client):  # noqa: pylint=invalid-name
    data = {'message': get_random_string()}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'message': 'Invalid input.', 'code': 'invalid',
        'detail': {
            'contact': [REQUIRED_FIELD_ERROR],
        }
    }


def test_api_create_comment(api_client):
    contact = ContactFactory.create()
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
        'name': get_random_string(),
    }

    data = {'message': get_random_string(), 'contact': payload}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data == {
        '_uid': res.data['_uid'],
        '_type': 'comment',
        'user': api_client.user.pk,
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


def test_api_create_comment_simple(api_client):
    contact = ContactFactory.create()
    data = {'message': get_random_string(), 'contact': contact.uid}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data == {
        '_uid': res.data['_uid'],
        '_type': 'comment',
        'user': api_client.user.pk,
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


def test_api_create_2_comments_for_one_contact(api_client):  # noqa: pylint=invalid-name
    contact = ContactFactory.create()
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
    }

    data = [
        {'message': get_random_string(), 'contact': payload},
        {'message': get_random_string(), 'contact': payload}, ]
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2
    assert contact.comments.all().count() == 2
