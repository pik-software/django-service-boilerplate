import logging
from typing import Union, Tuple

import celery
import requests
from celery import shared_task
from raven.contrib.django.raven_compat.models import client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.urls import resolve

from .consts import WEBHOOK_SUBSCRIPTION
from .models import Subscribe


LOGGER = logging.getLogger(__name__)


def _get_model_class(app_label, model_name):
    ct = ContentType.objects.get(app_label=app_label, model=model_name)
    return ct.model_class()


def _get_model_object(app_label, model_name, pk):
    model = _get_model_class(app_label, model_name)
    return model.objects.get(pk=pk)


def _do_async_fake_request(
        user_pk: Union[int, str], method: str, url: str, *,
        url_args=None, url_kwargs=None, data=None) -> Tuple[int, str]:
    """
    Do async requests to some site URLs from Celery workers.
    Use case: you have a some tricky and slow URL endpoint and you want
    to call this url from celery worker.
    
    Example:

        # some admin view function ...
        context = {}
        # ...
        url = urljoin(request.path, "../async-import/")
        async_request = async_fake_request.delay(
            request.user.id, 'post', url, data=data)
        # ...
        context['async_task_id'] = str(async_request.id)

    If you want to check the request status look at `get_task_result` API.

    :param user_pk: request user id
    :param method: request method (support only `get` and `post`)
    :param url: request url (should be available for `resolve` method)
    :param url_args: view function *args
    :param url_kwargs: view function **kwargs
    :param data: request POST data (only if method `post`)
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
    LOGGER.error('do fake request url="%s"', url)
    view_func, view_args, view_kwargs = resolve(url)
    view_kwargs.update(url_kwargs)

    if method == 'post':
        request = factory.post(url, data=data)
    else:
        request = factory.get(url, data=data)

    if user_pk:
        request.user = get_user_model().objects.get(pk=user_pk)

    request.is_async_fake_request = True

    response = view_func(request, *view_args, *url_args, **view_kwargs)  # noqa: pylint=not-callable
    response.render()
    code = response.status_code
    content = response.content.decode(response.charset)
    LOGGER.error('fake response status_code=%s %r', code, content)
    return code, content


def _transfer_webhook_data(webhook_url: str, data: str, **kwargs) -> None:
    requests.post(webhook_url, data=data, json=True, timeout=10, **kwargs)


@shared_task(bind=True, retry_backoff=True)  # retry in 5 seconds
def _replicate_history_process_webhook_subscriber(
        self: celery.Task, subscriber_pk,
        app_label: str, history_model_name: str,
        history_object_id: Union[str, int],
) -> str:
    try:
        subscriber: Subscribe = Subscribe.objects.get(pk=subscriber_pk)
    except Subscribe.DoesNotExist:
        return 'not_subscribed'

    webhook_url = subscriber.settings['webhook_url']
    api_version = subscriber.settings['api_version']
    webhook_cookies = subscriber.settings.get('webhook_cookies', None)
    webhook_headers = subscriber.settings.get('webhook_headers', None)
    webhook_auth = subscriber.settings.get('webhook_auth', None)
    user_pk = subscriber.user.pk

    hist_obj = _get_model_object(
        app_label, history_model_name, history_object_id)
    _type = hist_obj.history_object._meta.model_name
    event = hist_obj.history_type
    _uid = str(
        hist_obj.history_object.uid if hasattr(hist_obj.history_object, 'uid')
        else hist_obj.history_object.pk)

    LOGGER.error('webhook process event[%s] %s.%s.%s',
                 history_object_id, _type, event, _uid)

    _type = hist_obj.history_object._meta.model_name

    history_url = f'/api/v{api_version}/{_type}-list/history/'

    status, content = _do_async_fake_request(
        user_pk, 'get', history_url, data={'history_id': hist_obj.history_id})

    if status != 200:
        LOGGER.error(
            'webhook (retry) history status != 200; url = %r', history_url)
        raise self.retry()

    try:
        _transfer_webhook_data(
            webhook_url, content, auth=webhook_auth, headers=webhook_headers,
            cookies=webhook_cookies,
        )
        return 'ok'
    except Exception as exc:
        LOGGER.exception('webhook (retry) transfer error: %s', exc)
        client.captureException()
        raise self.retry(exc=exc)


@shared_task(bind=True)
def replicate_history(
        self: celery.Task,
        app_label: str, history_model_name: str,
        history_object_id: Union[str, int],
):
    """
    Example:
        
        replicate_history_task.delay(
            opts.app_label, opts.object_name, instance.history_id)

    """
    hist_obj = _get_model_object(
        app_label, history_model_name, history_object_id)
    _type = hist_obj.history_object._meta.model_name
    event = hist_obj.history_type
    _uid = hist_obj.history_object.pk

    events = [f'{_type}', f'{_type}.{event}', f'{_type}.{event}.{_uid}']
    subscribers = Subscribe.objects.filter(
        events__overlap=events, type=WEBHOOK_SUBSCRIPTION)

    for subscriber in subscribers:
        try:
            _replicate_history_process_webhook_subscriber.delay(
                subscriber.pk, app_label, history_model_name, history_object_id
            )
        except Exception as exc:
            LOGGER.exception(
                'replicate_history error: %s %s', subscriber.pk, exc)
            client.captureException()
