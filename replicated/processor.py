import logging

from .utils import _get_fields, _has_field
from .registry import _REPLICATED_MODEL_STORAGE


LOGGER = logging.getLogger(__name__)


class _ProcessHistoricalRecordError(Exception):
    def __init__(self, _type: str, _action: str, _uid: str, _version: int,
                 *args):
        self._type = _type
        self._action = _action
        self._uid = _uid
        self._version = _version
        super().__init__(*args)

    def __str__(self):
        message = super().__str__()
        return f"{self._type}.{self._action}.{self._uid}: " \
               f"{message} (v={self._version})"


def _process_historical_record(_type: str, _action: str, _uid: str,
                               _version: int, obj: dict):
    args = _type, _action, _uid, _version
    if _type not in _REPLICATED_MODEL_STORAGE:
        raise _ProcessHistoricalRecordError(*args, 'Unsupported _type')

    if _action in ['-']:
        return  # don't remove
    elif _action in ['+', '~']:
        pass
    else:
        raise _ProcessHistoricalRecordError(*args, 'Unsupported _action')

    model = _REPLICATED_MODEL_STORAGE[_type]
    fields = _get_fields(model)
    kwargs = {}

    for field in fields:
        if field.name in obj:
            value = obj[field.name]
            if field.is_relation:
                if isinstance(value, dict):
                    if '_uid' not in value or '_type' not in value:
                        raise _ProcessHistoricalRecordError(
                            *args, f'FK "{field.name}": no FK[_type] '
                                   f'or no FK[_uid]')

                    value = value['_uid']
                    if not isinstance(value, str):
                        raise _ProcessHistoricalRecordError(
                            *args, f'FK "{field.name}": type(_uid) != str')

                rel_model = field.remote_field.model._meta.concrete_model  # noqa
                rel_model_kwargs = {'uid': value} \
                    if _has_field(rel_model, 'uid') \
                    else {'pk': value}
                try:
                    value = rel_model.objects.get(**rel_model_kwargs)
                except rel_model.DoesNotExist:
                    raise _ProcessHistoricalRecordError(
                        *args, f'FK "{field.name}": DoesNotExists')
            kwargs[field.name] = value

    qs = model.objects.filter(uid=_uid)
    if qs.exists():
        instance = qs.first()
        if _version > instance.version:
            for key, val in kwargs.items():
                setattr(instance, key, val)
        else:
            LOGGER.warning("Received old %s version = %s (current %s)",
                           _type, _version, instance.version)
            return
    else:
        instance = model(**kwargs)

    instance.uid = _uid
    instance.autoincrement_version = False
    instance.version = _version
    instance.save()
