import logging

import celery
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from raven.contrib.django.raven_compat.models import client

from core.monitoring import alert
from .registry import get_replicating_model, _to_hist_obj
from ..consts import WEBHOOK_SUBSCRIPTION, ACTIONS
from ..models import Subscription
from ..utils import HistoryObject, ReplicatorDeliveryError, \
    ReplicatorSerializeError

LOGGER = logging.getLogger(__name__)


@shared_task(bind=True, retry_backoff=True, max_retries=10000)
def _process_webhook_subscription(
        self: celery.Task, subscription_pk, packed_history,
) -> str:
    try:
        subscription = Subscription.objects.select_related('user') \
            .get(pk=subscription_pk)
        hist_obj = HistoryObject.unpack(*packed_history)
    except Subscription.DoesNotExist:
        LOGGER.warning(
            "try to process does not exist subscription %s", subscription_pk)
        return 'subscription_does_not_exist'
    except ObjectDoesNotExist:
        LOGGER.warning(
            "try to process does not exist object %r", packed_history)
        return 'object_does_not_exist'

    retry = self.request.retries
    _type, _h_type, _uid = hist_obj.get_event_parts()
    _version = hist_obj._version
    ctx = {
        'name': subscription.name, 'user_pk': subscription.user.pk,
        'user_username': subscription.user.get_username(),
        '_type': _type, '_h_type': _h_type, '_uid': _uid,
        'retry': retry}

    LOGGER.info('webhook %r %s.%s.%s [hist_id=%s, v=%s] retry=%s',
                subscription.name, _type, _h_type, _uid,
                hist_obj.history_id, _version, retry)

    try:
        data = hist_obj.serialize(subscription)
    except ReplicatorSerializeError as exc:
        ctx.update(exc.ctx)
        ctx.update({'error': exc})
        alert("webhook '{name}' serialize error: {error}", **ctx)
        LOGGER.error('retry webhook %r: serialize error %r; retry=%s',
                     subscription.name, exc, retry)
        raise self.retry()
    except Exception as exc:  # noqa: pylint=broad-except
        LOGGER.exception(
            'webhook %r: error: %s; retry=%s', subscription.name, exc, retry)
        client.captureException()
        return 'unknown_serialize_error'

    try:
        hist_obj.deliver(subscription, data)
        return 'ok'
    except ReplicatorDeliveryError as exc:
        ctx.update(exc.ctx)
        ctx.update({'error': exc})
        alert("webhook '{name}' delivery error: {error}", **ctx)
        LOGGER.error(
            'retry webhook %r: remote response status!=200; retry=%s',
            subscription.name, retry)
        raise self.retry()
    except Exception as exc:  # noqa: pylint=broad-except
        LOGGER.exception(
            'webhook %r: error: %s; retry=%s', subscription.name, exc, retry)
        client.captureException()
        return 'unknown_delivery_error'


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
        hist_obj = HistoryObject.unpack(*packed_history)
        subscribers = hist_obj.get_subscribers(WEBHOOK_SUBSCRIPTION)
    except Exception as exc:
        LOGGER.exception('replicate_to_webhook error: %r', exc)
        client.captureException()
        raise self.retry(exc=exc)

    _type, _h_type, _uid = hist_obj.get_event_parts()
    LOGGER.info('webhooks %s.%s.%s [hist_id=%s, v=%s] retry=%s',
                _type, _h_type, _uid, hist_obj.history_id, hist_obj._version,
                retry)

    for subscriber in subscribers:
        try:
            _process_webhook_subscription.delay(subscriber.pk, packed_history)
        except Exception as exc:  # noqa: pylint=broad-except
            LOGGER.exception(
                'replicate_to_webhook error: %s %s', subscriber.pk, exc)
            client.captureException()


def _check_events(events):
    for event in events:
        splitted = event.split('.')
        model = get_replicating_model(splitted[0])
        if not model:
            raise ValueError('invalid_event_type')
        if len(splitted) >= 2 and splitted[1] not in ACTIONS:
            raise ValueError('invalid_event_action')
        if len(splitted) >= 3:
            if not model.objects.filter(uid=splitted[2]).exists():
                raise ValueError('invalid_event_uid')


@shared_task(bind=True)
def _re_replicate_webhook_subscription(
        self: celery.Task, subscription_pk, events,
) -> str:
    """
    Example:

        subscription = Subscription.objects.get(...)
        _re_replicate_webhook_subscription.delay(
            subscription.pk, subscription.events)

    """
    try:
        subscription = Subscription.objects.select_related('user')\
            .get(pk=subscription_pk)
    except Subscription.DoesNotExist:
        LOGGER.warning(
            "try to process does not exist subscription %s", subscription_pk)
        return 'subscription_does_not_exist'

    try:
        _check_events(events)
    except ValueError as exc:
        return str(exc)

    for event in events:
        splitted = event.split('.')
        q_set = get_replicating_model(splitted[0]).objects.order_by('pk')
        if len(splitted) >= 2:
            q_set = q_set.filter(history_type=splitted[1])
        if len(splitted) >= 3:
            q_set = q_set.filter(uid=splitted[2])

        for instance in q_set:
            packed_history = _to_hist_obj(instance).pack()
            _process_webhook_subscription.delay(
                subscription.pk, packed_history)
    return 'ok'
