from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework.fields import IntegerField

from core.api.lazy_field import LazyField
from core.api.serializers import StandardizedModelSerializer
from ..models import Contact, Comment, Category


class CategorySerializer(StandardizedModelSerializer):
    parent = LazyField('contacts.api.serializers.CategorySerializer',
                       required=False)

    class Meta:
        model = Category
        fields = (
            '_uid', '_type', '_version', 'created', 'updated',
            'name', 'parent')


class ContactSerializer(StandardizedModelSerializer):
    category = CategorySerializer(required=False)

    @staticmethod
    def update_schema(schema):
        schema['properties']['_uid']['description'] = ugettext(
            'Идентификатор Контакта')
        return schema

    class Meta:
        model = Contact
        fields = (
            '_uid', '_type', '_version', 'created', 'updated',
            'name', 'phones', 'emails',
            'order_index', 'category', 'contact_type')


class CommentSerializer(StandardizedModelSerializer):
    contact = ContactSerializer()

    user = IntegerField(source='user_id', required=False)

    update_schema = {'properties': {
            '_uid': {'description': _('Идентификатор Комментария')}}}

    def create(self, validated_data):
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Comment
        read_only_fields = ('user',)
        fields = (
            '_uid', '_type', '_version', 'created', 'updated',
            'user', 'contact', 'message')
