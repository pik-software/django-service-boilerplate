from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from simple_history.manager import HistoryManager

from .utils import _has_field
from .tasks import _replicate_to_webhook_subscribers

_REPLICATING_MODEL_STORAGE = {}
_REPLICATING_HISTORICAL_MODELS = set()


def replicating(_type: str):
    if _type in _REPLICATING_MODEL_STORAGE:
        raise ValueError('Model with same name already exists')

    _REPLICATING_MODEL_STORAGE[_type] = None

    def wrapper(model, _type=_type):
        if not issubclass(model, Model):
            raise TypeError('Required Model subclass')
        if not _has_field(model, 'version') or not _has_field(model, 'uid'):
            raise ValueError('Model should have uid and version fields')

        content_type = ContentType.objects.get_for_model(model).model
        if content_type != _type:
            raise ValueError('Model should have uid and version fields')

        if not hasattr(model, 'history'):
            raise ValueError('Model should have Model.history object')
        if not isinstance(model.history, HistoryManager):
            raise ValueError('Model.history is not a HistoryManager object')

        _REPLICATING_HISTORICAL_MODELS.add(model.history.model)
        _REPLICATING_MODEL_STORAGE[_type] = model
        return model
    return wrapper


def replicate(instance):
    model = instance._meta.concrete_model  # noqa
    opts = model._meta  # noqa
    _replicate_to_webhook_subscribers.delay(
        opts.app_label, opts.model_name, instance.history_id)


def is_replicating(model):
    content_type = ContentType.objects.get_for_model(model).model
    return content_type in _REPLICATING_MODEL_STORAGE


def _is_replicating_type(_type):
    return _type in _REPLICATING_MODEL_STORAGE


def _get_replication_model(_type):
    return _REPLICATING_MODEL_STORAGE.get(_type)


def _is_replicating_historical_model(model):
    return model in _REPLICATING_HISTORICAL_MODELS
