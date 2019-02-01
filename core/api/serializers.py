from typing import Optional, Union
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from rest_framework import serializers

from core.permitted_fields.api import PermittedFieldsSerializerMixIn


class StandardizedProtocolSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()
    _version = serializers.SerializerMethodField()

    @staticmethod
    def get__uid(obj) -> Optional[Union[str, UUID]]:
        if not hasattr(obj, 'uid'):
            if not hasattr(obj, 'pk'):
                return None
            return str(obj.pk)
        return obj.uid

    @staticmethod
    def get__type(obj) -> Optional[str]:
        if not isinstance(obj, Model):
            return None
        return ContentType.objects.get_for_model(type(obj)).model

    @staticmethod
    def get__version(obj) -> Optional[int]:
        if not hasattr(obj, 'version'):
            return None
        return obj.version


class StandardizedModelSerializer(StandardizedProtocolSerializer,
                                  PermittedFieldsSerializerMixIn,
                                  serializers.ModelSerializer):
    pass
