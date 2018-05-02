import logging
from typing import Union, Tuple

import celery
import requests
from celery import shared_task
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import resolve
from raven.contrib.django.raven_compat.models import client

from eventsourcing.utils import _get_event_name, _deserialize_history_instance
from ..consts import WEBHOOK_SUBSCRIPTION
from ..models import Subscription

LOGGER = logging.getLogger(__name__)


def _do_fake_request(
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


def _do_webhook_request(webhook_url: str, **kwargs) -> Tuple[int, str]:
    LOGGER.error('do webhook request url="%s"')
    response = requests.post(webhook_url, timeout=10, **kwargs)
    code, content = response.status_code, response.content
    LOGGER.error('webhook response status_code=%s %r', code, content)
    return code, content


@shared_task(bind=True, retry_backoff=True, max_retries=10000)
def _process_webhook_subscription(
        self: celery.Task, subscription_pk,
        app_label: str, history_model_name: str,
        history_object_id: Union[str, int],
) -> str:
    try:
        subscriber: Subscription = Subscription.objects.get(pk=subscription_pk)
    except Subscription.DoesNotExist:
        return 'not_subscribed'

    webhook_url = subscriber.settings['webhook_url']
    api_version = subscriber.settings['api_version']
    webhook_cookies = subscriber.settings.get('webhook_cookies', None)
    webhook_headers = subscriber.settings.get('webhook_headers', {})
    webhook_headers['content-type'] = 'application/json'
    webhook_auth = subscriber.settings.get('webhook_auth', None)
    if webhook_auth and isinstance(webhook_auth, list):
        # convert to requests auth tuple
        webhook_auth = tuple(webhook_auth)
    user_pk = subscriber.user.pk

    hist_obj = _deserialize_history_instance(
        app_label, history_model_name, history_object_id)
    _type, _action, _uid = _get_event_name(hist_obj)

    LOGGER.error('webhook process event[%s] %s.%s.%s',
                 history_object_id, _type, _action, _uid)

    history_url = f'/api/v{api_version}/{_type}-list/history/'

    status, content = _do_fake_request(
        user_pk, 'get', history_url, data={'history_id': hist_obj.history_id})

    if status != 200:
        LOGGER.error(
            'webhook (retry) history status != 200; url = %r', history_url)
        raise self.retry()

    try:
        webhook_status, webhook_response = _do_webhook_request(
            webhook_url, data=content, auth=webhook_auth,
            headers=webhook_headers, cookies=webhook_cookies,
        )
        return 'ok'
    except Exception as exc:
        LOGGER.exception('webhook (retry) transfer error: %s', exc)
        client.captureException()
        raise self.retry(exc=exc)


@shared_task(bind=True)
def _replicate_to_webhook_subscribers(
        self: celery.Task,
        app_label: str, history_model_name: str,
        history_object_id: Union[str, int],
):
    """
    Example:
        
        replicate_history_task.delay(
            opts.app_label, opts.object_name, instance.history_id)

    """
    hist_obj = _deserialize_history_instance(
        app_label, history_model_name, history_object_id)
    _type, _action, _uid = _get_event_name(hist_obj)

    events = [f'{_type}', f'{_type}.{_action}', f'{_type}.{_action}.{_uid}']
    subscribers = Subscription.objects.filter(
        events__overlap=events, type=WEBHOOK_SUBSCRIPTION)

    for subscriber in subscribers:
        try:
            _process_webhook_subscription.delay(
                subscriber.pk, app_label, history_model_name, history_object_id
            )
        except Exception as exc:
            LOGGER.exception(
                'replicate_history error: %s %s', subscriber.pk, exc)
            client.captureException()
