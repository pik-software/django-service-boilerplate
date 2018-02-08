import django.test
import pytest
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture
def logged_user_client(client: django.test.Client):
    user = create_user()
    client.force_login(user)
    return client


def test_api_authorization(client):
    res = client.get('/api/v1/')
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_create(logged_user_client):
    data = {'name': get_random_string()}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_create_bulk(logged_user_client):
    data = [{'name': get_random_string()}, {'name': get_random_string()}]
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2


def test_api_create_without_name(logged_user_client):
    data = {'noname': get_random_string()}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'name': [{'code': 'required', 'message': 'Это поле обязательно.'}]},
        'message': 'Invalid input.'}


def test_api_create_with_extra_field(logged_user_client):
    data = {'name': get_random_string(), 'fooo': 'no'}
    res = logged_user_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
