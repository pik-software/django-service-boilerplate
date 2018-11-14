from rest_framework.fields import IntegerField

from core.api.fields import PrimaryKeyModelSerializerField
from core.api.serializers import StandardizedModelSerializer
from ..models import Contact, Comment


class ContactSerializer(StandardizedModelSerializer):
    class Meta:
        model = Contact
        read_only_fields = (
            '_uid', '_type', '_version',
        )
        fields = (
            '_uid', '_type', '_version', 'name', 'phones', 'emails',
            'order_index',
        )


class CommentSerializer(StandardizedModelSerializer):
    contact = PrimaryKeyModelSerializerField(
        ContactSerializer,
        allowed_objects=lambda serializer: serializer.Meta.model.objects.all())

    user = IntegerField(source='user_id', required=False)

    def create(self, validated_data):
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Comment
        read_only_fields = (
            '_uid', '_type', '_version', 'user',
        )
        fields = (
            '_uid', '_type', '_version', 'user', 'contact', 'message',
        )
