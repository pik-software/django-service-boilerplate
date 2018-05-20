import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models.signals import post_save
from django.conf import settings as dj_settings
from simple_history.manager import HistoryManager

from ..models import Subscription
from ..utils import _pack_history_instance, _get_event_names
from .serializer import _check_serialize_problem, \
    SerializeHistoricalInstanceError, serialize
from .utils import _has_field

LOGGER = logging.getLogger(__name__)

_LATEST_API_VERSION_SETTING = 'REST_FRAMEWORK_LATEST_API_VERSION'
_REPLICATING_MODEL_STORAGE = {}
_REPLICATING_MODEL_SET = set()


def replicating(_type: str):
    if _type in _REPLICATING_MODEL_STORAGE:
        raise ValueError('Model with same name already exists')

    _REPLICATING_MODEL_STORAGE[_type] = None

    def wrapper(model, _type=_type):
        if not issubclass(model, Model):
            raise TypeError('Required Model subclass')
        if not _has_field(model, 'version') or not _has_field(model, 'uid'):
            raise ValueError('Model should have uid and version fields')

        # Unfortunately, we can't use ContentType here
        content_type = model._meta.concrete_model._meta.model_name  # noqa
        if content_type != _type:
            raise ValueError(f'Use @replicating("{content_type}", ...)')

        if not hasattr(model, 'history'):
            raise ValueError('Model should have Model.history object')
        if not isinstance(model.history, HistoryManager):
            raise ValueError('Model.history is not a HistoryManager object')

        historical = model.history.model
        if historical in _REPLICATING_MODEL_SET:
            raise ValueError('Model is already replicating')

        _REPLICATING_MODEL_SET.add(historical)
        _REPLICATING_MODEL_STORAGE[_type] = historical
        post_save.connect(_post_save_historical_model, sender=historical)
        return model
    return wrapper


def replicate(instance) -> None:
    from .tasks import _replicate_to_webhook_subscribers  # noqa

    packed_history = _pack_history_instance(instance)
    _replicate_to_webhook_subscribers.apply_async(
        args=(packed_history, ), countdown=0.5)


def re_replicate(subscription, events):
    from .tasks import _re_replicate_subscription  # noqa

    _re_replicate_subscription.apply_async(
        args=(subscription.pk, events), countdown=0.5)


def is_replicating(model) -> bool:
    content_type = ContentType.objects.get_for_model(model)
    return content_type.model in _REPLICATING_MODEL_STORAGE


def check_replication(user, settings=None):
    if not settings:
        version = getattr(dj_settings, _LATEST_API_VERSION_SETTING, '1')
        settings = {'api_version': version}

    result = {}
    for _type, model in _REPLICATING_MODEL_STORAGE.items():
        try:
            result[_type] = 'OK'
            _check_serialize_problem(user, settings, _type)
            last_obj = model.objects.last()
            if last_obj:
                serialize(user, settings, last_obj)
        except SerializeHistoricalInstanceError as exc:
            result[_type] = f'ERROR: {exc}'
    return result


def _get_replication_model(_type):
    return _REPLICATING_MODEL_STORAGE.get(_type)


def _get_all_replication_models():
    return list(_REPLICATING_MODEL_STORAGE.items())


def _post_save_historical_model(sender, instance, created, **kwargs):
    if not created:
        raise RuntimeError('Historical changes detected! WTF?')

    events = _get_event_names(instance)
    subscribers = Subscription.objects.filter(events__overlap=events)
    if subscribers.exists():
        LOGGER.info('replicate %s [hist=%s]', events[-1], instance.history_id)
        replicate(instance)
