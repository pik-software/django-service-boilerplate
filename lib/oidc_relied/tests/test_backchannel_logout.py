from importlib import import_module
from unittest.mock import patch, Mock

from jwkest import JWKESTException
import pytest

import django.test
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse


@pytest.fixture
def backchannel_logout_url():
    return reverse('oidc_backchannel_logout', kwargs={'backend': 'pik'})


@pytest.fixture
def session_store():
    return import_module(settings.SESSION_ENGINE).SessionStore()


def test_wrong_method(backchannel_logout_url):
    client = django.test.Client()
    response = client.get(backchannel_logout_url)
    assert response.status_code == 405


@patch('lib.oidc_relied.backends.PIKOpenIdConnectAuth.'
       'validate_and_return_logout_token',
       Mock(return_value={'sid': 'test_token'}))
def test_success(backchannel_logout_url, session_store):
    cache.set('oidc_userdata_test_token', 'testuserinfo')
    client = django.test.Client()
    session_key = client.session.session_key
    cache.set('oidc_token_session_test_token', session_key)
    response = client.post(backchannel_logout_url)
    assert response.status_code == 200
    assert cache.get('oidc_userdata_test_token') is None
    assert not client.session.exists(client.session.session_key)
    assert client.session.session_key != session_key


@patch('social_core.backends.open_id_connect.JWS.verify_compact',
       Mock(side_effect=JWKESTException('Signature verification failed')))
def test_wrong_sign(backchannel_logout_url):
    cache.set('oidc_userdata_test_token', 'testuserinfo')
    client = django.test.Client()
    response = client.post(backchannel_logout_url)
    assert response.status_code == 403
    assert cache.get('oidc_userdata_test_token') == 'testuserinfo'


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
    assert response.status_code == 403
    assert response.content == b'Token error: Invalid audience'
    assert cache.get('oidc_userdata_test_token') == 'testuserinfo'


def test_missing_token(backchannel_logout_url):
    cache.set('oidc_userdata_test_token', 'testuserinfo')
    client = django.test.Client()
    response = client.post(backchannel_logout_url)
    assert response.status_code == 403
    assert cache.get('oidc_userdata_test_token') == 'testuserinfo'
