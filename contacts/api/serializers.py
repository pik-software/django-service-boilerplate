from core.api.fields import PrimaryKeyModelSerializerField
from core.api.serializers import StandardizedModelSerializer
from ..models import Contact, Comment


class ContactSerializer(StandardizedModelSerializer):
    class Meta:
        model = Contact
        read_only_fields = (
            '_uid', '_type',
        )
        fields = (
            '_uid', '_type', 'name', 'phones', 'emails', 'order_index',
        )


class CommentSerializer(StandardizedModelSerializer):
    contact = PrimaryKeyModelSerializerField(
        ContactSerializer,
        allowed_objects=lambda serializer: serializer.Meta.model.objects.all()
    )

    class Meta:
        model = Comment
        read_only_fields = (
            '_uid', '_type', 'user',
        )
        fields = (
            '_uid', '_type', 'user', 'contact', 'message',
        )
