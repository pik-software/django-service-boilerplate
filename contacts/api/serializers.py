from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    _uid = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()

    def get__uid(self, obj):  # noqa: pylint: no-self-use
        return obj.uid

    def get__type(self, obj):  # noqa: pylint: no-self-use
        return ContentType.objects.get_for_model(type(obj)).model

    class Meta:
        model = Contact
        fields = (
            '_uid', '_type', 'name', 'phones', 'emails', 'order_index',
        )
