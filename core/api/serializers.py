from collections import OrderedDict
from typing import Optional, Union
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ListSerializer, ModelSerializer

from core.permitted_fields.api import PermittedFieldsSerializerMixIn


class SettableNestedSerializerMixIn:
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist':
            _('Недопустимый uid "{uid_value}" - объект не существует.'),
        'incorrect_uid_type':
            _('Некорректный тип uid. Ожидался uid, получен {data_type}.'),
        'incorrect_type':
            _('Некорректный тип объекта. Ожидался {expected_object_type}, '
              'получен {object_type}.'),
    }

    def run_validation(self, data=empty):
        if not self.parent:
            return super().run_validation(data)
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        # We are using this class as serializer and serializer field, so need
        #  to keep both behaviors.
        return self.to_internal_value(data)

    def to_internal_value(self, request_data):
        if not self.parent or isinstance(self.parent, ListSerializer):
            return super().to_internal_value(request_data)

        if isinstance(request_data, (dict, OrderedDict)):
            object_type = request_data.get('_type')
            expected = ContentType.objects.get_for_model(self.Meta.model).model
            if object_type != expected:
                self.fail('incorrect_type',
                          expected_object_type=expected,
                          object_type=object_type)
            uid_value = request_data.get('_uid')
        else:
            uid_value = request_data
        try:
            return self.Meta.model.objects.get(uid=uid_value)
        except self.Meta.model.DoesNotExist:
            self.fail('does_not_exist', uid_value=uid_value)
        except (TypeError, ValueError):
            self.fail('incorrect_uid_type', data_type=type(uid_value).__name__)


class StandardizedProtocolSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()
    _version = serializers.SerializerMethodField()

    def get__uid(self, obj) -> Optional[Union[str, UUID]]:
        if not hasattr(obj, 'uid'):
            if not hasattr(obj, 'pk'):
                return None
            return str(obj.pk)
        return obj.uid

    def get__type(self, obj) -> Optional[str]:
        if not isinstance(obj, Model):
            return None
        return ContentType.objects.get_for_model(type(obj)).model

    def get__version(self, obj) -> Optional[int]:
        if not hasattr(obj, 'version'):
            return None
        return obj.version


class LabeledModelSerializerMixIn:
    """ Default DRF ModelSerializer has different nature than DRF Field

        1. DRF ModelSerializer does't handle labels and help_texts as expected.
        2. DRF ModelSerializer has 2 different behaviours:
            - initialized for direct use within viewset,
            - initialized and binded for use within other serializer as field.
        3. So label and help_text handling should provided on two stages:
            - `__init__()` for using within viewset,
            - `bind()` for use as field withing other serializer.

        This MixIn:
            - on `__init__()`:
                - sets label and help_text to model values if not provided,
                - saves `is_set`=True if provided;
            - on `bind()`:
                - sets label and help_text to parent model field values if
                `is_set`=`False`.
    """

    _label_is_set = False
    _help_text_is_set = False

    def __init__(self, *args, **kwargs):
        opts = self.Meta.model._meta  # noqa: protected-access

        if 'label' not in kwargs:
            kwargs['label'] = opts.verbose_name
        else:
            self._label_is_set = True

        if 'help_text' not in kwargs:
            kwargs['help_text'] = getattr(self.Meta.model, 'help_text', None)
        else:
            self._help_text_is_set = True

        self.label_plural = opts.verbose_name_plural
        if 'label_plural' in kwargs:
            self.label_plural = kwargs.pop('label_plural')

        super().__init__(*args, **kwargs)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if isinstance(parent, ModelSerializer):
            opts = parent.Meta.model._meta  # noqa: protected-access
            if not self._label_is_set:
                self.label = opts.get_field(self.source).verbose_name
            if not self._help_text_is_set:
                self.help_text = opts.get_field(self.source).help_text


class StandardizedModelSerializer(LabeledModelSerializerMixIn,
                                  SettableNestedSerializerMixIn,
                                  PermittedFieldsSerializerMixIn,
                                  StandardizedProtocolSerializer):
    pass
