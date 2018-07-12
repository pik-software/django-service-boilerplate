import logging

from .registry import _get_replicated_model
from ..consts import UPDATED_ACTION, DELETED_ACTION, CREATED_ACTION
from ..utils import _has_field, _get_fields

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
        if field.name not in obj:
            continue

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


def _process_deleted_historical_record(model, _type, _uid, _version):
    try:
        instance = model._base_manager.get(uid=_uid)  # noqa
        if _version >= instance.version:
            instance.delete()
        else:
            LOGGER.error("[D] %s.-.%s (v=%s): old version (current v=%s)",
                         _type, _uid, _version, instance.version)
    except model.DoesNotExist:
        LOGGER.warning("[D] %s.-.%s (v=%s): does not exists",
                       _type, _uid, _version)


def _process_created_historical_record(
        model, model_attributes, _type, _uid, _version):
    q_set = model._base_manager.filter(uid=_uid)  # noqa
    if q_set.exists():
        instance = q_set.last()
        LOGGER.warning("[C] %s.+.%s (v=%s): already exists (current v=%s)",
                       _type, _uid, _version, instance.version)
        return

    instance = model(**model_attributes)
    instance.uid = _uid
    instance.autoincrement_version = False
    instance.version = _version
    instance.save()


def _process_updated_historical_record(
        model, model_attributes, _type, _uid, _version):
    try:
        instance = model._base_manager.get(uid=_uid)  # noqa
        if _version > instance.version:
            for key, val in model_attributes.items():
                setattr(instance, key, val)
        else:
            LOGGER.warning("[U] %s.+.%s (v=%s): old version (current v=%s)",
                           _type, _uid, _version, instance.version)
            return
    except model.DoesNotExist:
        LOGGER.error('[U] %s.-.%s (v=%s): does not exists',
                     _type, _uid, _version)
        return

    instance.uid = _uid
    instance.autoincrement_version = False
    instance.version = _version
    instance.save()


def _process_historical_record(_type: str, _action: str, _uid: str,
                               _version: int, hist_record: dict):
    ctx = _type, _action, _uid, _version
    model = _get_replicated_model(_type)
    if not model:
        raise _ProcessHistoricalRecordError(*ctx, 'Unsupported _type')

    LOGGER.info('process_historical_record %s.%s.%s (v=%s)', *ctx)
    if _action in [DELETED_ACTION]:
        _process_deleted_historical_record(model, _type, _uid, _version)
    elif _action in [CREATED_ACTION]:
        model_attributes = _prepare_model_attributes(model, hist_record, ctx)
        _process_created_historical_record(
            model, model_attributes, _type, _uid, _version)
    elif _action in [UPDATED_ACTION]:
        model_attributes = _prepare_model_attributes(model, hist_record, ctx)
        _process_updated_historical_record(
            model, model_attributes, _type, _uid, _version)
    else:
        raise _ProcessHistoricalRecordError(*ctx, 'Unsupported _action')
