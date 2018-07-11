import logging
from typing import List, Tuple

from django.db.models import Model
from django.db.models.signals import post_save, post_delete
from simple_history.manager import HistoryManager

from .utils import _has_field
from ..utils import HistoryObject

LOGGER = logging.getLogger(__name__)

_HISTORY_TYPE_TO_MODEL = {}
_MODEL_TO_HISTORY_TYPE = {}
_REPLICATING_MODEL_SET = set()


def replicating(_type: str):
    if _type in _HISTORY_TYPE_TO_MODEL:
        raise ValueError('Model with same name already exists')

    _HISTORY_TYPE_TO_MODEL[_type] = None

    def wrapper(model, _type=_type):
        if not issubclass(model, Model):
            raise TypeError('Required Model subclass')
        if not _has_field(model, 'version') or not _has_field(model, 'uid'):
            raise ValueError('Model should have uid and version fields')

        # Unfortunately, we can't use ContentType here
        content_type = model._meta.concrete_model._meta.model_name  # noqa
        if content_type != _type:
            raise ValueError(f'Use @replicating("{content_type}", ...)')

        # Prevent double replication
        if model in _REPLICATING_MODEL_SET:
            raise ValueError('Model is already replicating')
        _REPLICATING_MODEL_SET.add(model)

        is_historical = (
            hasattr(model, 'history') and
            isinstance(model.history, HistoryManager))

        if is_historical:
            hook_model = model.history.model
            post_save_hook = _post_save_historical_model
            post_delete_hook = _post_delete_historical_model
        else:
            hook_model = model
            post_save_hook = _post_save_model
            post_delete_hook = _post_delete_model

        _HISTORY_TYPE_TO_MODEL[_type] = hook_model
        _MODEL_TO_HISTORY_TYPE[hook_model] = _type
        post_save.connect(post_save_hook, sender=hook_model)
        post_delete.connect(post_delete_hook, sender=hook_model)
        return model
    return wrapper


def is_replicating(model: Model) -> bool:
    return model in _REPLICATING_MODEL_SET


def get_replicating_model(_type: str) -> Model:
    return _HISTORY_TYPE_TO_MODEL.get(_type)


def get_all_replicating_models() -> List[Tuple[str, Model]]:
    return list(_HISTORY_TYPE_TO_MODEL.items())


def _get_event_parts(instance):
    _uid = str(instance.uid)
    _type = _MODEL_TO_HISTORY_TYPE[instance._meta.concrete_model]  # noqa
    _version = instance.version
    return _uid, _type, _version


def _to_hist_obj(instance, *, history_id=None, history_type=None):
    return HistoryObject(
        instance, history_id, history_type,
        *_get_event_parts(instance))


# SIGNAL LISTENERS


def _post_save_historical_model(sender, instance, created, **kwargs):
    if not created:
        raise RuntimeError('Historical changes detected! WTF?')

    _uid, _type, _version = _get_event_parts(instance)
    hist_obj = HistoryObject(
        instance, None, instance.history_type,
        _uid, _type, _version)

    hist_obj.replicate()


def _post_delete_historical_model(sender, instance, **kwargs):
    raise RuntimeError('Historical delete detected! WTF?')


def _post_save_model(sender, instance, created, **kwargs):
    _uid, _type, _version = _get_event_parts(instance)
    hist_obj = HistoryObject(
        instance, None, '+' if created else '~',
        _uid, _type, _version)

    hist_obj.replicate()


def _post_delete_model(sender, instance, **kwargs):
    _uid, _type, _version = _get_event_parts(instance)
    hist_obj = HistoryObject(
        instance, None, '-',
        _uid, _type, _version)

    hist_obj.replicate()
