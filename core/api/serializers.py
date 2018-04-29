from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from rest_framework import serializers


class StandardizedModelSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()

    def get__uid(self, obj) -> Optional[str]:  # noqa: pylint=no-self-use
        if not hasattr(obj, 'uid'):
            if not hasattr(obj, 'pk'):
                return None
            return str(obj.pk)
        return obj.uid

    def get__type(self, obj) -> Optional[str]:  # noqa: pylint=no-self-use
        if not isinstance(obj, Model):
            return None
        return ContentType.objects.get_for_model(type(obj)).model
