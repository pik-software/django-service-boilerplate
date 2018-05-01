from django.db.models import Model

from .utils import _has_field

_REPLICATED_MODEL_STORAGE = {}


def replicated(_type: str):
    if _type in _REPLICATED_MODEL_STORAGE:
        raise ValueError('Model with same name already exists')

    _REPLICATED_MODEL_STORAGE[_type] = None

    def wrapper(model, _type=_type):
        if not issubclass(model, Model):
            raise TypeError('Required Model subclass')
        if not _has_field(model, 'version') or not _has_field(model, 'uid'):
            raise ValueError('Model should have uid and version fields')
        _REPLICATED_MODEL_STORAGE[_type] = model
        return model

    return wrapper


def is_replicated(model):
    return model in _REPLICATED_MODEL_STORAGE.values()
