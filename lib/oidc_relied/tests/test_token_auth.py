from functools import partial
from unittest.mock import patch

import django.test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from requests import Response, HTTPError
from rest_framework import status

from contacts.models import Contact


class HTTPResponse(Response):
    def __init__(self, content, status_code=200, **headers):
        super().__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code
        self.headers.update(headers)


class JsonResponse(Response):

    def __init__(self, json, status_code=200):
        super().__init__()
        self._json = json
        self.status_code = status_code

    def json(self, **kwargs):
        return self._json


make_api_request = partial(django.test.Client().get, "/api/v1/contact-list/",  # noqa invalid-name
                           **{'HTTP_AUTHORIZATION': 'Bearer pik token'})


@patch("social_core.backends.base.BaseAuth.request")
def test_correct_token_api(oidc_request_mock):
    content_type = ContentType.objects.get_for_model(Contact)
    perm = Permission.objects.get(content_type=content_type,
                                  codename="view_contact")
    default_group = Group.objects.create(name='default')
    default_group.permissions.add(perm)

    def side_effect(url, *args, **kwargs):
        if url.endswith("/openid/.well-known/openid-configuration"):
            return JsonResponse(dict(
                issuer="/openid",
                authorization_endpoint="/openid/authorize",
                token_endpoint="/openid/token",
                userinfo_endpoint="/openid/userinfo",
                end_session_endpoint="/openid/end-session",
                response_types_supported=["code", "id_token", "id_token token",
                                          "code token", "code id_token",
                                          "code id_token token"],
                jwks_uri="/openid/jwks",
                id_token_signing_alg_values_supported=["HS256", "RS256"],
                subject_types_supported=["public"],
                token_endpoint_auth_methods_supported=["client_secret_post",
                                                       "client_secret_basic"]))

        if url.endswith("/openid/userinfo"):
            return JsonResponse(dict(
                sub="newUserSub",
                nickname="newUserNick",
                preferred_username="newUserPreferredUserName",
                email='newUser@email.com',
                roles=[dict(name="testrole")]
            ))

        raise Http404

    oidc_request_mock.side_effect = side_effect

    response = make_api_request()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dict(
        count=0, page=1, page_next=None, page_previous=None, page_size=20,
        pages=1, results=[])

    oidc_request_mock.side_effect = Exception("NonCached request")
    response = make_api_request()
    assert response.json() == dict(
        count=0, page=1, page_next=None, page_previous=None, page_size=20,
        pages=1, results=[])

    user = get_user_model().objects.last()
    assert (set(user.groups.values_list('name', flat=True)) ==
            {'testrole', 'default'})
    assert user.username == "newUserPreferredUserName"


@patch("social_core.backends.base.BaseAuth.request")
def test_wrong_token_api(oidc_request_mock):
    oidc_request_mock.side_effect = HTTPError(
        'Error', response=HTTPResponse('error', 401, **{
            "WWW-Authenticate": (
                'error="invalid_token", '
                'error_description="The access token provided '
                'is expired, revoked, malformed, or invalid '
                'for other reasons')}))
    resp = make_api_request()
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED,
                                status.HTTP_403_FORBIDDEN)
    assert resp.json() == {
        'code': 'invalid_token',
        'message': ('The access token provided is expired, revoked, '
                    'malformed, or invalid for other reasons')}
