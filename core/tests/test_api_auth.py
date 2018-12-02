from django.utils.crypto import get_random_string
from rest_framework import status

from core.tasks.fixtures import create_user


REQUIRED_FIELD_ERROR = {'message': 'Это поле обязательно.', 'code': 'required'}


def test_api_token_auth_without_data(anon_api_client):  # noqa: pylint=invalid-name
    res = anon_api_client.post('/api-token-auth/', data={})

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'username': [REQUIRED_FIELD_ERROR],
            'password': [REQUIRED_FIELD_ERROR],
        },
        'message': 'Invalid input.'}


def test_api_token_auth(anon_api_client):
    user = create_user()
    username = getattr(user, user.USERNAME_FIELD)
    password = get_random_string()
    user.set_password(password)
    user.save()

    res = anon_api_client.post('/api-token-auth/', data={
        'username': username, 'password': password})

    assert res.status_code == status.HTTP_200_OK
    assert 'token' in res.data
