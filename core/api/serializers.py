from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class StandardizedModelSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()

    def get__uid(self, obj):  # noqa: pylint=no-self-use
        if not hasattr(obj, 'uid'):
            return obj.id
        return obj.uid

    def get__type(self, obj) -> str:  # noqa: pylint=no-self-use
        return ContentType.objects.get_for_model(type(obj)).model
