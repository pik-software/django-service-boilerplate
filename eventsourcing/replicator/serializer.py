from typing import Tuple, Optional
import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.test import RequestFactory
from django.urls import resolve

from ..utils import _get_splitted_event_name


LOGGER = logging.getLogger(__name__)


class SerializeHistoricalInstanceError(Exception):
    pass


def serialize(user, settings: dict, historical_instance) -> str:
    _type, _, _ = _get_splitted_event_name(historical_instance)
    api_version = settings['api_version']
    history_url = f'/api/v{api_version}/{_type}-list/history/'
    history_id = historical_instance.history_id
    status, content = _process_fake_request(
        user.pk, 'get', history_url, data={'history_id': history_id})
    if status != 200:
        raise SerializeHistoricalInstanceError(
            f'serialize api status = {status}')
    return content


def _check_serialize_problem(user, settings: dict, _type):
    # TODO: really we should check the serialize API schema here!
    api_version = settings['api_version']
    history_url = f'/api/v{api_version}/{_type}-list/history/'
    status, content = _process_fake_request(
        user, 'get', history_url)
    if status != 200:
        raise SerializeHistoricalInstanceError(
            f'serialize api status = {status}')
    if not content:
        raise SerializeHistoricalInstanceError('serialize api no content')


def _process_fake_request(
        user: Optional[models.Model], method: str, url: str, *,
        url_args=None, url_kwargs=None, data=None) -> Tuple[int, str]:
    """
    Do fake requests to some site URLs.

    Use case: you have a some tricky and slow URL endpoint and you want
    to process this url logic from celery worker.

    Example:

        # some admin view function ...
        context = {}
        # ...
        url = urljoin(path, "../async-import/")
        status, content = _process_fake_request(
            user.pk, 'post', url, data=data)
        # ...

    :param user_pk: request user id
    :param method: request method (support only `get` and `post`)
    :param url: request url (should be available for `resolve` method)
    :param url_args: view function *args
    :param url_kwargs: view function **kwargs
    :param data: request data
    :return: [status_code, decoded_response_content]
    """
    if not url_kwargs:
        url_kwargs = {}
    if not url_args:
        url_args = tuple()
    method = method.lower()
    if method not in ['post', 'get']:
        raise ValueError('invalid async_fake_request method')
    if method in ['post'] and data is None:
        raise ValueError(
            'unexpected async_fake_request post request '
            'without data'
        )

    factory = RequestFactory()
    LOGGER.info('do fake request url=%r', url)
    view_func, view_args, view_kwargs = resolve(url)
    view_kwargs.update(url_kwargs)

    if method == 'post':
        request = factory.post(url, data=data)
    else:
        request = factory.get(url, data=data)

    if user:
        request.user = get_user_model().objects.get(pk=user.pk)

    request.is_fake_request = True

    response = view_func(request, *view_args, *url_args, **view_kwargs)  # noqa: pylint=not-callable
    response.render()
    code = response.status_code
    content = response.content.decode(response.charset)
    LOGGER.info('fake response status_code=%s %r', code, content)
    return code, content
