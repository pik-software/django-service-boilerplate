from functools import partial
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.admin import site
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import resolve_url
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from social_core.actions import do_complete
from social_core.backends.oauth import OAuthAuth
from social_django.utils import psa
from social_django.views import NAMESPACE, _do_login


def oidc_admin_login(request: HttpRequest) -> HttpResponseRedirect:
    if settings.OIDC_PIK_CLIENT_ID is None:
        return site.login(request)

    if not request.user.is_authenticated:
        args = f"?{urlencode(request.GET)}" if request.GET else ""
        return HttpResponseRedirect(f"{resolve_url(settings.LOGIN_URL)}{args}")

    if not request.user.is_active:
        raise PermissionDenied(_("Данный пользователь отключен"))

    if not request.user.is_staff:
        raise PermissionDenied(_("У вас нет доступа к данному интерфейсу"))

    url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
    return HttpResponseRedirect(url)


@partial(partial, backend="pik")
@psa()
def oidc_admin_logout(request: HttpRequest, backend: str) -> HttpResponse:
    if settings.OIDC_PIK_CLIENT_ID is None:
        return site.login(request)

    return request.backend.logout()


@csrf_exempt
@psa()
@require_POST
def oidc_backchannel_logout(request: HttpRequest, backend: str,
                            *args, **kwargs) -> HttpResponse:
    logout_token = request.POST.get('logout_token', '')
    return request.backend.backchannel_logout(logout_token)


@never_cache
@csrf_exempt
@psa('{0}:complete'.format(NAMESPACE))
def complete(request: HttpRequest, backend: str,
             *args, **kwargs) -> HttpResponse:
    """ Authentication complete view with custom _do_login method, saving token
    to session link """
    return do_complete(request.backend, _do_save_session_login, request.user,
                       redirect_name=REDIRECT_FIELD_NAME, request=request,
                       *args, **kwargs)


def _do_save_session_login(backend: OAuthAuth, user, social_user) -> None:
    """ Login user with saving result token to session link in order to provide
    backchannel logut """
    _do_login(backend, user, social_user)
    if hasattr(backend, 'save_token_session'):
        backend.save_token_session()
