from collections import OrderedDict

from core.api.serializers import StandardizedModelSerializer


class HistorySerializerMixIn:
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields  # noqa

        history_field_names = (
            'history_id', 'history_date', 'history_change_reason',
            'history_user_id', 'history_type')
        for field_name in history_field_names:
            try:
                value = getattr(instance, field_name)
                ret[field_name] = value
            except Exception:  # noqa: pylint=broad-except
                continue

        for field in fields:
            get_simplified_nested_serializer(field)
            try:
                attribute = field.get_attribute(instance)
                if attribute is not None:
                    ret[field.field_name] = field.to_representation(
                        attribute)
                else:
                    ret[field.field_name] = None
            except AttributeError:
                ret[field.field_name] = None

        return ret


def get_simplified_nested_serializer(serializer):
    if isinstance(serializer, StandardizedModelSerializer):
        for _name, _field in list(serializer.fields.items()):
            if _name not in ('_uid', '_type'):
                serializer.fields.pop(_name)


def get_history_serializer_class(model_name, serializer_class):
    name = f'{model_name}Serializer'
    return type(name, (HistorySerializerMixIn, serializer_class), {})
