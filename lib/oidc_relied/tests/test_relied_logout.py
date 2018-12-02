from unittest.mock import patch, Mock
from urllib.parse import urlencode


import django.test
from django.urls import reverse

from rest_framework import status


@django.test.override_settings(OIDC_PIK_CLIENT_ID="TEST_CLIENT_ID")
@patch("social_core.backends.open_id_connect.OpenIdConnectAuth.oidc_config",
       Mock(return_value={
           'end_session_endpoint': 'http://op/openid/end-session/'}))
def test_logout(api_client):
    api_client.session['id_token'] = '{testidtoken}'
    resp = api_client.get(reverse('admin:logout'))
    assert resp.status_code == status.HTTP_302_FOUND
    assert resp['Location'] == 'http://op/openid/end-session/?{}'.format(
        urlencode({'post_logout_redirect_uri': 'http://testserver/logout/'}))
    assert api_client.session.get('id_token') is None
