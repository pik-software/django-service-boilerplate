from django.http import Http404
from django.utils.translation import ugettext as _
from rest_framework import exceptions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import set_rollback


def standardized_handler(exc, context):  # noqa
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.

    Example:

        REST_FRAMEWORK = {
            ...
            'EXCEPTION_HANDLER':
                'core.api.exception_handler.standardized_handler',
            ...
        }
    """
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        code = exc.default_code
        if hasattr(exc.detail, 'code') and exc.detail.code:
            code = exc.detail.code

        if isinstance(exc.detail, (list, dict)):
            data = {
                'code': code,
                'detail': exc.get_full_details(),
                'message': str(exc.default_detail),
            }
        else:
            data = {
                'code': code,
                'message': str(exc.detail),
            }

        set_rollback()

        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        data = {
            'message': _('Not found.'),
            'code': 'not_found'}
        set_rollback()
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, PermissionDenied):
        data = {
            'message': _('Permission denied.'),
            'code': 'permission_denied'}
        set_rollback()
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    return None
