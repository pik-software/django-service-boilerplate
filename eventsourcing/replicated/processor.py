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


def _prepare_model_attributes(model, hist_record, ctx) -> dict:
    fields = _get_fields(model)
    attributes = {}
    obj = hist_record

    for field in fields:
        if field.name in obj:
            value = obj[field.name]
            if field.is_relation:
                if isinstance(value, dict):
                    if '_uid' not in value or '_type' not in value:
                        mag = f'FK "{field.name}": no FK[_type] or no FK[_uid]'
                        raise _ProcessHistoricalRecordError(*ctx, mag)

                    value = value['_uid']
                    if not isinstance(value, str):
                        msg = f'FK "{field.name}": type(_uid) != str'
                        raise _ProcessHistoricalRecordError(*ctx, msg)

                rel_model = field.remote_field.model._meta.concrete_model  # noqa
                rel_model_kwargs = {'uid': value} \
                    if _has_field(rel_model, 'uid') \
                    else {'pk': value}
                try:
                    value = rel_model.objects.get(**rel_model_kwargs)
                except rel_model.DoesNotExist:
                    msg = f'FK "{field.name}": DoesNotExists'
                    raise _ProcessHistoricalRecordError(*ctx, msg)
            attributes[field.name] = value
    return attributes


def _process_historical_record(_type: str, _action: str, _uid: str,
                               _version: int, hist_record: dict):
    ctx = _type, _action, _uid, _version
    if _type not in _REPLICATED_MODEL_STORAGE:
        raise _ProcessHistoricalRecordError(*ctx, 'Unsupported _type')

    if _action in ['-']:
        # TODO: realize remove!?
        return  # don't remove
    elif _action in ['+', '~']:
        pass
    else:
        raise _ProcessHistoricalRecordError(*ctx, 'Unsupported _action')

    model = _REPLICATED_MODEL_STORAGE[_type]
    model_attributes = _prepare_model_attributes(model, hist_record, ctx)

    try:
        instance = model.objects.get(uid=_uid)
        if _version > instance.version:
            for key, val in model_attributes.items():
                setattr(instance, key, val)
        else:
            LOGGER.warning("Received old %s version = %s (current %s)",
                           _type, _version, instance.version)
            return
    except model.DoesNotExist:
        instance = model(**model_attributes)

    instance.uid = _uid
    instance.autoincrement_version = False
    instance.version = _version
    instance.save()
