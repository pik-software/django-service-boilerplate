from rest_framework import status


def test_api_user_without_data(anon_api_client):
    res = anon_api_client.get('/api-user/')
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.data['code'] == 'not_authenticated'


def test_api_user_auth(api_user, api_client):
    username = getattr(api_user, api_user.USERNAME_FIELD)
    res = api_client.get('/api-user/')

    assert res.status_code == status.HTTP_200_OK
    assert res.data == {'email': api_user.email, 'username': username}
