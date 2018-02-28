import pytest
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user

REQUIRED_FIELD_ERROR = {'message': 'Это поле обязательно.', 'code': 'required'}


@pytest.fixture()
def client():
    return APIClient()


def test_api_token_auth_without_data(client):
    res = client.post('/api-token-auth/', data={})

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'username': [REQUIRED_FIELD_ERROR],
            'password': [REQUIRED_FIELD_ERROR],
        },
        'message': 'Invalid input.'}


def test_api_token_auth(client):
    user = create_user()
    username = getattr(user, user.USERNAME_FIELD)
    password = get_random_string()
    user.set_password(password)
    user.save()

    res = client.post('/api-token-auth/', data={
        'username': username, 'password': password})

    assert res.status_code == status.HTTP_200_OK
    assert 'token' in res.data
