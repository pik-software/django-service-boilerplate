from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

from core.models import Dated, PUided, Versioned, Owned
from .consts import SUBSCRIPTION_TYPES


class Subscribe(PUided, Dated, Versioned, Owned):
    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=SUBSCRIPTION_TYPES)
    settings = JSONField()
    events = ArrayField(models.CharField(max_length=200))

    history = HistoricalRecords()

    def clean(self):
        super().clean()

    class Meta:
        unique_together = (('name', 'type'), )
        verbose_name = _("Подписка")
        verbose_name_plural = _("Подписки")


def create_or_update_subscription(user, name, type, settings, events):
    obj, is_new = Subscribe.objects.get_or_create(
        {'settings': settings, 'events': events, 'user': user},
        name=name, type=type)

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


@receiver(post_save, dispatch_uid='historical-instance-saved')
def historical_instance_saved(sender, instance, created, **kwargs):
    """
    Automatically triggers "created" and "updated" actions.
    """
    opts = instance._meta.concrete_model._meta
    if not opts.object_name.startswith('Historical'):
        return
    if not created:
        raise RuntimeError('Historical changes detected! WTF?')

    model = '.'.join([opts.app_label, opts.model_name])
    print('!', model, instance, instance.history_id)

    _type = instance.history_object._meta.model_name
    event = instance.history_type
    _uid = str(
        instance.history_object.uid if hasattr(instance.history_object, 'uid')
        else instance.history_object.pk)
    events = [f'{_type}', f'{_type}.{event}', f'{_type}.{event}.{_uid}']
    subscribers = Subscribe.objects.filter(events__overlap=events)
    if subscribers.exists():
        from replication.tasks import replicate_history  # noqa
        replicate_history.delay(
            opts.app_label, opts.model_name, instance.history_id,
        )
