from django.http import HttpResponseForbidden
from social_core.exceptions import SocialAuthBaseException
from social_django.middleware import SocialAuthExceptionMiddleware


class OIDCExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if not isinstance(exception, SocialAuthBaseException):
            return None
        return HttpResponseForbidden(self.get_message(request, exception))
