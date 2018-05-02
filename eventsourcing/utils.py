from django.contrib.contenttypes.models import ContentType


def _get_event_name(instance):
    _type = instance.history_object._meta.model_name  # noqa
    _action = instance.history_type
    _uid = str(
        instance.history_object.uid if hasattr(instance.history_object, 'uid')
        else instance.history_object.pk)
    return _type, _action, _uid


def _serialize_history_instance(instance):
    model = instance._meta.concrete_model  # noqa
    opts = model._meta  # noqa
    return opts.app_label, opts.model_name, instance.history_id


def _deserialize_history_instance(app_label, model_name, pk):
    ct = ContentType.objects.get(app_label=app_label, model=model_name)
    model = ct.model_class()
    return model.objects.get(pk=pk)
