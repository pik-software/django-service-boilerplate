import logging
from time import time
from typing import Optional, Union, Tuple, List, Iterable

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model

from .models import Subscription

LOGGER = logging.getLogger(__name__)


class ReplicatorSerializeError(Exception):
    def __init__(self, message: str, ctx: Optional[dict] = None) -> None:
        self.ctx = ctx or {}
        super().__init__(message)


class ReplicatorDeliveryError(Exception):
    def __init__(self, message: str, ctx: Optional[dict] = None) -> None:
        self.ctx = ctx or {}
        super().__init__(message)


class HistoryObject:
    def __init__(self, instance: Model,
                 history_id: Optional[int], history_type: Optional[str],
                 _uid: str, _type: str, _version: Optional[int]):
        if not history_id:
            if hasattr(instance, 'history_id'):
                history_id = instance.history_id
            else:
                history_id = int(time() * 1000)
        if not history_type:
            if hasattr(instance, 'history_type'):
                history_type = instance.history_type
            else:
                history_type = '+'
        self.history_id = history_id
        self.history_type = history_type
        self.instance_uid = _uid
        self.instance_type = _type
        self.instance_version = _version
        self.instance = instance

    def __repr__(self):
        app_label, model, key, _h_id, _h_type, _uid, _type, _version = \
            self.pack()
        return f'<HistoryObject({app_label}.{model}.{key}, ' \
               f'{_h_id!r}, {_h_type!r}, {_uid!r}, {_type!r}, {_version!r})>'

    def __eq__(self, other):
        return repr(self) == repr(other)

    def get_event_names(self) -> List[str]:
        _type, _h_type = self.instance_type, self.history_type
        _uid = self.instance_uid
        return [f'{_type}', f'{_type}.{_h_type}', f'{_type}.{_h_type}.{_uid}']

    def get_event_parts(self) -> Tuple[str, str, str]:
        return self.instance_type, self.history_type, self.instance_uid

    def pack(self) -> Tuple[str, str, Union[str, int],
                            int, str,
                            str, str, Optional[int]]:
        model = self.instance._meta.concrete_model  # noqa
        c_type = ContentType.objects.get_for_model(model)
        return (
            c_type.app_label, c_type.model, self.instance.pk,
            self.history_id, self.history_type,
            self.instance_uid, self.instance_type, self.instance_version)

    @classmethod
    def unpack(cls, app_label: str, model: str, pk: Union[str, int],  # noqa: pylint=invalid-name
               history_id: int, history_type: str,
               _uid: str, _type: str, _version: Optional[int]) \
            -> 'HistoryObject':
        c_type = ContentType.objects.get(app_label=app_label, model=model)
        model_class = c_type.model_class()
        instance = model_class.objects.get(pk=pk)
        return HistoryObject(
            instance, history_id, history_type, _uid, _type, _version)

    def get_subscribers(self, subscription_type: Optional[int] = None) \
            -> Iterable[Subscription]:
        events = self.get_event_names()
        subscribers = Subscription.objects.filter(events__overlap=events)
        if subscription_type:
            subscribers = subscribers.filter(type=subscription_type)
        return subscribers

    def replicate(self, subscription=None) -> None:
        from .replicator.replicator import _replicate

        if subscription:
            assert self.get_subscribers().filter(pk=subscription.pk).exists()
            _replicate(self, subscription)
        else:
            events = self.get_event_names()
            subscribers = self.get_subscribers()
            if subscribers.exists():
                LOGGER.info('replicate %s [hist_id=%s, v=%s]',
                            events[-1], self.history_id, self.instance_version)
                _replicate(self)

    @classmethod
    def re_replicate(cls, subscription: Subscription, events: List[str]) \
            -> None:
        from .replicator.replicator import _re_replicate

        _re_replicate(subscription, events)

    def serialize(self, subscription: Subscription) -> str:
        from .replicator.serializer import _serialize

        return _serialize(subscription.user, subscription.settings, self)

    def deliver(self, subscription: Subscription, serialized_data: str) \
            -> None:
        from .replicator.deliverer import _deliver

        _deliver(subscription.user, subscription.settings, serialized_data)


def _has_field(model, field):
    try:
        model._meta.get_field(field)  # noqa
        return True
    except FieldDoesNotExist:
        return False


def _get_fields(model):
    return model._meta.get_fields()  # noqa
