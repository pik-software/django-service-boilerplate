from importlib import import_module
from unittest.mock import patch, Mock

from jwkest import JWKESTException
import pytest

import django.test
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def backchannel_logout_url():
    return reverse('oidc_backchannel_logout', kwargs={'backend': 'pik'})


@pytest.fixture
def session_store():
    return import_module(settings.SESSION_ENGINE).SessionStore()


def test_wrong_method(backchannel_logout_url):
    client = django.test.Client()
    response = client.get(backchannel_logout_url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@patch('lib.oidc_relied.backends.PIKOpenIdConnectAuth.'
       'validate_and_return_logout_token',
       Mock(return_value={'sid': 'test_sid'}))
def test_success(backchannel_logout_url, session_store):
    cache.set('oidc_sid_userdata_test_sid', ['userdata'])
    cache.set('oidc_sid_tokens_test_sid', ['token'])
    client = django.test.Client()
    session_key = client.session.session_key
    cache.set('oidc_sid_sessions_test_sid', [session_key])
    response = client.post(backchannel_logout_url)
    assert response.status_code == status.HTTP_200_OK
    assert cache.get('oidc_sessions_test_token') is None
    assert cache.get('oidc_userdata_test_token') is None
    assert cache.get('oidc_tokens_test_token') is None
    assert not client.session.exists(client.session.session_key)


@patch('social_core.backends.open_id_connect.JWS.verify_compact',
       Mock(side_effect=JWKESTException('Signature verification failed')))
def test_wrong_sign(backchannel_logout_url):
    client = django.test.Client()
    response = client.post(backchannel_logout_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch('lib.oidc_relied.backends.JWS.verify_compact',
       Mock(return_value={'aud': '24', 'iss': 'test_provider'}))
@patch('lib.oidc_relied.backends.PIKOpenIdConnectAuth.get_jwks_keys',
       Mock())
@patch('lib.oidc_relied.backends.PIKOpenIdConnectAuth.id_token_issuer',
       Mock(return_value="test_provider"))
@patch('lib.oidc_relied.backends.PIKOpenIdConnectAuth.get_key_and_secret',
       Mock(return_value=('42', '')))
def test_wrong_client(backchannel_logout_url):
    cache.set('oidc_userdata_test_token', 'testuserinfo')
    client = django.test.Client()
    response = client.post(backchannel_logout_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.content == b'Token error: Invalid audience'
    assert cache.get('oidc_userdata_test_token') == 'testuserinfo'


def test_missing_token(backchannel_logout_url):
    cache.set('oidc_userdata_test_token', 'testuserinfo')
    client = django.test.Client()
    response = client.post(backchannel_logout_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert cache.get('oidc_userdata_test_token') == 'testuserinfo'
