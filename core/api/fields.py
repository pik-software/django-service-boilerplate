from collections import OrderedDict

from deprecated import deprecated
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.db.models import FieldDoesNotExist
from rest_framework import serializers
from rest_framework.fields import empty

from ..api.serializers import StandardizedModelSerializer


def _get_model_field(model, field):
    try:
        return model._meta.get_field(field)  # noqa
    except FieldDoesNotExist:
        return None


@deprecated
class PrimaryKeyModelSerializerField(serializers.Field):
    """
    DEPLRECATED use inner serializers! (see `contacts.api.serializers` example)

    Use it if you want to use ModelSerializer inside other ModelSerializer.

    Use `allowed_objects` function to restrict access to nested objects
    for some users. To check access during creation and modification
    of nested objects.

    Example:

        def allow_all_objects(serializer) -> QuerySet:
            return serializer.Meta.model.objects.all()

        def allow_only_user_objects(serializer) -> QuerySet:
            return serializer.Meta.model.objects.all().filter(
                user=serializer.context['request'].user)

        class ContactSerializer(StandardizedModelSerializer):
            class Meta:
                model = Contact
                read_only_fields = ('_uid', '_type', 'user')
                fields = ('_uid', '_type', 'user', 'name')

        class CommentSerializer(StandardizedModelSerializer):
            contact = PrimaryKeyModelSerializerField(
                ContactSerializer,
                allowed_objects=allow_only_user_objects,  # !!
            )

            class Meta:
                model = Comment
                read_only_fields = ('_uid', '_type', 'user')
                fields = ('_uid', '_type', 'user', 'contact', 'message')
    """
    default_error_messages = {
        'required': _(
            'This field is required.'),
        'does_not_exist': _(
            'Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _(
            'Incorrect type. Expected pk value, received {data_type}.'),
        'no_uid': _('No _uid value'),
        'no_type': _('No _type value'),
        'incorrect_type_value': _('Invalid _type value, expect {data_type}'),
    }

    def __init__(self, serializer, **kwargs):
        if not issubclass(serializer, StandardizedModelSerializer):
            raise TypeError(
                "serializer argument should be a StandardizedModelSerializer "
                "instance")

        self._model = model = getattr(serializer, 'Meta').model
        if _get_model_field(model, 'uid'):
            pk_field = serializers.UUIDField(format='hex')
            pk_field.field_name = 'uid'
        else:
            # If you really want, You can add pk_field argument (similar to
            # rest_framework.serializers.PrimaryKeyRelatedField argument).
            # At the moment, I do not see this as an urgent need.
            raise TypeError("unknown pk_field for model")

        get_allowed_objects = kwargs.pop('allowed_objects', None)
        self._get_allowed_objects = get_allowed_objects
        if get_allowed_objects and not callable(get_allowed_objects):
            raise TypeError("get_allowed_objects argument should be callable")

        self._pk_field = pk_field
        self._serializer = serializer

        has_get_allowed_objects = bool(self._get_allowed_objects)
        is_read_only = kwargs.get('read_only', None)
        is_many = kwargs.get('many', None)
        assert isinstance(self._pk_field.field_name, str), (
            'no pk_field.field_name'
        )
        assert not is_many, (
            "PrimaryKeyNestedModelSerializerField fields should "
            "not set many=True"
        )
        assert has_get_allowed_objects or is_read_only, (
            'PrimaryKeyNestedModelSerializerField field must provide '
            'a `allowed_objects` callable argument or set read_only=`True`.'
        )
        super().__init__(**kwargs)

    def _get_serializer(self, instance=None, data=empty):
        assert self.parent, (
            "you should use PrimaryKeyNestedModelSerializerField "
            "inside StandardizedModelSerializer"
        )
        assert self.parent.context.get('request'), (
            "no self.parent.context.get('request'). "
            "you should use PrimaryKeyNestedModelSerializerField "
            "inside StandardizedModelSerializer"
        )
        return self._serializer(
            instance=instance, data=data, context=self.parent.context)

    def bind(self, field_name, parent):
        # just assert it!
        assert isinstance(parent, StandardizedModelSerializer), (
            "you should use PrimaryKeyNestedModelSerializerField "
            "inside StandardizedModelSerializer"
        )
        return super().bind(field_name, parent)

    def to_internal_value(self, data):
        if isinstance(data, (dict, OrderedDict)):
            _uid = data.get('_uid')
            _type = data.get('_type')
            if not _uid:
                self.fail('no_uid')
            if not _type:
                self.fail('no_type')
            model_type = ContentType.objects.get_for_model(self._model).model
            if _type != model_type:
                self.fail('incorrect_type_value', data_type=model_type)
            data = _uid
        try:
            data = self._pk_field.to_internal_value(data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)
        try:
            serializer = self._get_serializer()
            return self._get_allowed_objects(serializer).get(**{
                self._pk_field.field_name: data})
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)

    def to_representation(self, value):
        return self._get_serializer(value).data
