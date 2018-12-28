import logging

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.core.models import BasePHistorical, Owned

from .consts import SUBSCRIPTION_TYPES

LOGGER = logging.getLogger(__name__)


class Subscription(BasePHistorical, Owned):
    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=SUBSCRIPTION_TYPES)
    settings = JSONField()
    events = ArrayField(models.CharField(max_length=200))

    class Meta:
        unique_together = (('name', 'type'), )
        verbose_name = _("Подписка")
        verbose_name_plural = _("Подписки")


def subscribe(user, name, type_, settings, events):
    obj, is_new = Subscription.objects.get_or_create(
        {'settings': settings, 'events': events, 'user': user},
        name=name, type=type_)

    if is_new:
        return obj

    if obj.user != user:
        raise ValueError('You are trying update not your subscription')

    extra_events = [x for x in events if x not in obj.events]

    if not extra_events and obj.settings == settings:
        return obj

    obj.settings = settings
    obj.events.extend(extra_events)
    obj.save()
    return obj


def unsubscribe(user, name, type_, events):
    obj, is_new = Subscription.objects.get_or_create(
        {'settings': {}, 'events': [], 'user': user},
        name=name, type=type_)

    if is_new:
        return obj

    if obj.user != user:
        raise ValueError('You are trying update not your subscription')

    new_events = [x for x in obj.events if x not in events]

    if new_events == obj.events:
        return obj

    obj.events = new_events
    obj.save()
    return obj
