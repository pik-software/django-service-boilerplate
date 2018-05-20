import logging
from typing import Tuple

import celery
from celery import shared_task
from raven.contrib.django.raven_compat.models import client
import requests

from core.monitoring import alert
from ..utils import _get_splitted_event_name, \
    _unpack_history_instance, _get_event_names, _pack_history_instance
from ..consts import WEBHOOK_SUBSCRIPTION, ACTIONS
from ..models import Subscription
from .serializer import serialize, SerializeHistoricalInstanceError

LOGGER = logging.getLogger(__name__)


def _prepare_webhook_request_kwargs(settings):
    webhook_url = settings['webhook_url']
    webhook_cookies = settings.get('webhook_cookies', None)
    webhook_headers = settings.get('webhook_headers', {})
    webhook_headers['content-type'] = 'application/json'
    webhook_auth = settings.get('webhook_auth', None)
    if webhook_auth and isinstance(webhook_auth, list):
        # convert to requests auth tuple
        webhook_auth = tuple(webhook_auth)
    return webhook_url, dict(
        auth=webhook_auth, headers=webhook_headers, cookies=webhook_cookies,
    )


def _run_request_to_webhook(
        user, settings, serialized_data
) -> Tuple[int, str]:
    url, kwargs = _prepare_webhook_request_kwargs(settings)
    data = serialized_data.encode('utf-8')
    LOGGER.info('do webhook request url="%s"; %r', url, kwargs)
    response = requests.post(url, data=data, timeout=10, **kwargs)
    code, content = response.status_code, response.content
    LOGGER.info('webhook response status_code=%s %r', code, content)
    return code, content


@shared_task(bind=True, retry_backoff=True, max_retries=10000)
def _process_webhook_subscription(
        self: celery.Task, subscription_pk, packed_history,
) -> str:
    try:
        subscription = Subscription.objects.select_related('user')\
            .get(pk=subscription_pk)
    except Subscription.DoesNotExist:
        LOGGER.warning(
            "try to process does not exist subscription %s", subscription_pk)
        return 'subscription_does_not_exist'

    hist_obj = _unpack_history_instance(packed_history)
    retry = self.request.retries
    _type, _action, _uid = _get_splitted_event_name(hist_obj)
    _version = hist_obj.version
    ctx = {
        'name': subscription.name, 'user_pk': subscription.user.pk,
        'user_username': subscription.user.get_username(),
        '_type': _type, '_action': _action, '_uid': _uid,
        'retry': retry}

    LOGGER.info('webhook %r %s.%s.%s (v=%s) retry=%s',
                subscription.name, _type, _action, _uid, _version, retry)

    try:
        data = serialize(subscription.user, subscription.settings, hist_obj)
    except SerializeHistoricalInstanceError as exc:
        ctx.update({'error': exc})
        alert("webhook '{name}' serialize error: {error}", **ctx)
        LOGGER.error('retry webhook %r: serialize error %r; retry=%s',
                     subscription.name, exc, retry)
        raise self.retry()

    try:
        response_status, response_content = _run_request_to_webhook(
            subscription.user, subscription.settings, data)

        if response_status != 200:
            ctx.update({
                'response_status': response_status,
                'response_content': response_content})
            alert("webhook '{name}' response status={response_status}", **ctx)
            LOGGER.error(
                'retry webhook %r: remote response status!=200; retry=%s',
                subscription.name, retry)
            raise self.retry()

        return 'ok'
    except Exception as exc:
        LOGGER.exception(
            'retry webhook %r: remote server error: %s; retry=%s',
            subscription.name, exc, retry)
        client.captureException()
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=1,
             retry_backoff=True)
def _replicate_to_webhook_subscribers(
        self: celery.Task,
        packed_history,
):
    """
    Example:

        packed_history = _pack_history_instance(instance)
        _replicate_to_webhook_subscribers.delay(packed_history)

    """
    retry = self.request.retries
    try:
        hist_obj = _unpack_history_instance(packed_history)
        events = _get_event_names(hist_obj)
        subscribers = Subscription.objects.filter(
            events__overlap=events, type=WEBHOOK_SUBSCRIPTION)
    except Exception as exc:
        LOGGER.exception('replicate_to_webhook error: %r', exc)
        client.captureException()
        raise self.retry(exc=exc)

    LOGGER.info('replicate_to_webhook %s (v=%s) retry=%s',
                events[-1], hist_obj.version, retry)

    for subscriber in subscribers:
        try:
            _process_webhook_subscription.delay(subscriber.pk, packed_history)
        except Exception as exc:  # noqa: pylint=broad-except
            LOGGER.exception(
                'replicate_to_webhook error: %s %s', subscriber.pk, exc)
            client.captureException()


@shared_task(bind=True)
def _re_replicate_subscription(
        self: celery.Task, subscription_pk, events,
) -> str:
    try:
        subscription = Subscription.objects.select_related('user')\
            .get(pk=subscription_pk)
    except Subscription.DoesNotExist:
        LOGGER.warning(
            "try to process does not exist subscription %s", subscription_pk)
        return 'subscription_does_not_exist'

    from .registry import _get_replication_model  # noqa

    for event in events:
        splitted = event.split('.')
        model = _get_replication_model(splitted[0])
        if not model:
            return 'invalid_event_type'
        if len(splitted) >= 2 and splitted[1] not in ACTIONS:
            return 'invalid_event_action'
        if len(splitted) >= 3:
            if not model.objects.filter(uid=splitted[2]).exists():
                return 'invalid_event_uid'

    if subscription.type == WEBHOOK_SUBSCRIPTION:
        for event in events:
            splitted = event.split('.')
            q_set = _get_replication_model(splitted[0]).objects.order_by('pk')
            if len(splitted) >= 2:
                q_set = q_set.filter(history_type=splitted[1])
            if len(splitted) >= 3:
                q_set = q_set.filter(uid=splitted[2])

            for instance in q_set:
                packed_history = _pack_history_instance(instance)
                _process_webhook_subscription.delay(
                    subscription.pk, packed_history)
    return 'ok'
