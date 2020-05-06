from collections import OrderedDict
from typing import Optional, Union
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model
from django_restql.mixins import DynamicFieldsMixin
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ListSerializer

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

    @swagger_serializer_method(serializer_or_field=serializers.UUIDField)
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


class StandardizedModelSerializer(DynamicFieldsMixin,
                                  SettableNestedSerializerMixIn,
                                  PermittedFieldsSerializerMixIn,
                                  StandardizedProtocolSerializer):
    pass
