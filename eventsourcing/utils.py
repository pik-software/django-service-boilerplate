from django.contrib.contenttypes.models import ContentType


def _get_splitted_event_name(historical_instance):
    _type = historical_instance.history_object._meta.model_name  # noqa
    _action = historical_instance.history_type
    _uid = str(
        historical_instance.history_object.uid
        if hasattr(historical_instance.history_object, 'uid')
        else historical_instance.history_object.pk)
    return _type, _action, _uid


def _get_event_names(historical_instance):
    _type, _action, _uid = _get_splitted_event_name(historical_instance)
    return [f'{_type}', f'{_type}.{_action}', f'{_type}.{_action}.{_uid}']


def _pack_history_instance(historical_instance):
    model = historical_instance._meta.concrete_model  # noqa
    ct = ContentType.objects.get_for_model(model)
    return ct.app_label, ct.model, historical_instance.history_id


def _unpack_history_instance(packed_history):
    app_label, model_name, pk = packed_history
    ct = ContentType.objects.get(app_label=app_label, model=model_name)
    model = ct.model_class()
    return model.objects.get(pk=pk)
