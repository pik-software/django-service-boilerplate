from unittest.mock import patch, Mock
from urllib.parse import urlencode

import pytest

import django.test
from django.urls import reverse

from pik.core.tests import create_user
from rest_framework import status


@pytest.fixture
def user():
    return create_user(email="oidcclient@email.com", password="oidcpassword")


@pytest.fixture
def logged_user_client(client: django.test.Client, user):
    client.force_login(user)
    return client


@django.test.override_settings(OIDC_PIK_CLIENT_ID="TEST_CLIENT_ID")
@patch("social_core.backends.open_id_connect.OpenIdConnectAuth.oidc_config",
       Mock(return_value={
           'end_session_endpoint': 'http://op/openid/end-session/'}))
def test_logout(logged_user_client):
    logged_user_client.session['id_token'] = '{testidtoken}'
    resp = logged_user_client.get(reverse('admin:logout'))
    assert resp.status_code == status.HTTP_302_FOUND
    assert resp['Location'] == 'http://op/openid/end-session/?{}'.format(
        urlencode({'post_logout_redirect_uri': 'http://testserver/logout/'}))
    assert logged_user_client.session.get('id_token') is None
