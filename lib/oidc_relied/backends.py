import datetime
from calendar import timegm
from importlib import import_module
from typing import Any, Tuple

from jwkest.jws import JWS
from jwkest import JWKESTException

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import resolve, Resolver404, reverse
from django.utils.http import urlencode
from django.core.cache import cache

from pik.core.cache import cachedmethod
from requests import HTTPError
from requests.utils import parse_dict_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.exceptions import AuthTokenError


PIK_OIDC_PROVIDER_NAME = 'pik'


class PIKOpenIdConnectAuth(OpenIdConnectAuth):  # noqa: abstract-method
    OIDC_ENDPOINT = settings.OIDC_PIK_ENDPOINT
    name = PIK_OIDC_PROVIDER_NAME
    USERDATA_KEY = 'oidc_userdata_{access_token}'
    SID_SESSIONS_KEY = 'oidc_sid_sessions_{sid}'
    SID_TOKENS_KEY = 'oidc_sid_tokens_{sid}'
    RESPONSE_TYPE = 'code'
    EXTRA_DATA = OpenIdConnectAuth.EXTRA_DATA + [('sid', 'sid')]
    GET_ALL_EXTRA_DATA = True

    def do_auth(self, access_token: str, *args, **kwargs) -> Any:
        user = super().do_auth(access_token, *args, **kwargs)

        id_token_hint = kwargs.get('response', {}).get('id_token')
        if user.is_authenticated and id_token_hint is not None:
            self.access_token = access_token  # noqa attribute-defined-outside-init
            self.strategy.session_set('id_token_hint', id_token_hint)

        sid = user.social_user.extra_data.get('sid')
        if sid:
            key = self.SID_TOKENS_KEY.format(sid=sid)
            values = cache.get(key, [])
            if access_token not in values:
                values.append(access_token)
                cache.set(key, values, timeout=settings.SESSION_COOKIE_AGE)

        return user

    def save_logout_artefacts(self) -> None:
        """ Save sid to token/session links, . Needed to provide backchannel
            logout. """

        if not self.id_token:
            return

        sid = self.id_token.get('sid')

        if not sid:
            return

        key = self.SID_SESSIONS_KEY.format(sid=sid)
        values = cache.get(key, [])
        values.append(self.strategy.session.session_key)
        cache.set(key, values, timeout=settings.SESSION_COOKIE_AGE)

    def validate_and_return_logout_token(self, jws: str) -> dict:  # noqa invalid-name
        """ Validated logout_token """
        try:
            # Decode the JWT and raise an error if the sig is invalid
            id_token = JWS().verify_compact(jws.encode('utf-8'),
                                            self.get_jwks_keys())
        except JWKESTException:
            raise AuthTokenError(self, 'Signature verification failed')

        self.validate_logout_claims(id_token)

        return id_token

    def validate_logout_claims(self, id_token: dict) -> None:
        """ Validated logout_token claims
            http://openid.net/specs/openid-connect-backchannel-1_0.html#LogoutToken
         """

        if id_token['iss'] != self.id_token_issuer():
            raise AuthTokenError(self, 'Invalid issuer')

        client_id, _ = self.get_key_and_secret()

        if isinstance(id_token['aud'], str):
            id_token['aud'] = [id_token['aud']]

        if client_id not in id_token['aud']:
            raise AuthTokenError(self, 'Invalid audience')

        if len(id_token['aud']) > 1 and 'azp' not in id_token:
            raise AuthTokenError(self, 'Incorrect logout_token: azp')

        utc_timestamp = timegm(datetime.datetime.utcnow().utctimetuple())
        if 'exp' in id_token and utc_timestamp > id_token['exp']:
            raise AuthTokenError(self, 'Signature has expired')

        # Verify the token was issued in the last 10 minutes
        iat_leeway = self.setting('ID_TOKEN_MAX_AGE', self.ID_TOKEN_MAX_AGE)
        if utc_timestamp > id_token['iat'] + iat_leeway:
            raise AuthTokenError(self, 'Incorrect logout_token: iat')

        if 'sid' not in id_token:
            raise AuthTokenError(self, 'Incorrect logout_token: sid')

    def backchannel_logout(self, logout_token: str) -> HttpResponse:
        """ Process backchannel logout """

        logout_token = self.validate_and_return_logout_token(logout_token)
        sid = logout_token.get('sid')

        if sid:
            cache_key = self.SID_TOKENS_KEY.format(sid=sid)
            for access_token in cache.get(cache_key, ()):
                cache.delete(self.USERDATA_KEY.format(
                    access_token=access_token))
            cache.delete(cache_key)

            cache_key = self.SID_SESSIONS_KEY.format(sid=sid)
            for session in cache.get(cache_key, ()):
                engine = import_module(settings.SESSION_ENGINE)
                engine.SessionStore(session).delete(session)
            cache.delete(cache_key)

        return HttpResponse()

    def logout(self) -> HttpResponseRedirect:
        endpoint = self.oidc_config().get('end_session_endpoint')
        params = {'post_logout_redirect_uri':
                  self.strategy.build_absolute_uri(reverse('logout'))}
        id_token_hint = self.strategy.session_get('id_token_hint', None)
        if id_token_hint is not None:
            params['id_token_hint'] = id_token_hint

        logout(self.strategy.request)

        if endpoint is None:
            return HttpResponseRedirect(reverse('logout'))
        return HttpResponseRedirect(f'{endpoint}?{urlencode(params)}')

    def get_user_by_username(self, username: str) -> Any:
        user_model = self.strategy.storage.user.user_model()
        username_field = getattr(user_model, 'USERNAME_FIELD', 'username')
        users = user_model.objects.filter(**{f'{username_field}': username})
        return users.first()

    @cachedmethod(USERDATA_KEY)
    def user_data(self, access_token: str, *args, **kwargs) -> dict:
        return super().user_data(access_token, *args, **kwargs)

    def get_key_and_secret(self) -> Tuple[str, str]:
        return (self.setting('OIDC_PIK_CLIENT_ID'),
                self.setting('OIDC_PIK_CLIENT_SECRET'))

    def request(self, url: str, *args, **kwargs) -> dict:  # noqa: arguments-differ
        """ Providing PIK API standardized auth error response for for API
        views by `WWW-Authenticate` header parsing.

        Example:

            If Provider returns for /api/:

                HTTPError(headers={'WWW-Authenticate': error="oh_error",
                    error_description="Oh Error!"})

            Transforming into:

                AuthenticationFailed({"code": "oh_error",
                    message: "Oh Error!"})

        """

        try:
            return super().request(url, *args, **kwargs)
        except HTTPError as exc:
            if exc.response.status_code != 401:
                raise

            if 'WWW-Authenticate' not in exc.response.headers:
                raise

            try:
                view = resolve(self.strategy.request.path)
            except Resolver404:
                raise exc

            view = getattr(view.func, 'cls')
            if not issubclass(view, APIView):
                raise

            auth = parse_dict_header(exc.response.headers['WWW-Authenticate'])

            if not ('error' in auth and 'error_description' in auth):
                raise

            raise AuthenticationFailed(auth['error_description'].strip('"\''),
                                       auth['error'].strip('"\''))
