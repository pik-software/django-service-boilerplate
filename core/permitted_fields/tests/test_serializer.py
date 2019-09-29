from unittest.mock import Mock, patch

import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.permitted_fields.api import PermittedFieldsSerializerMixIn


@patch('rest_framework.serializers.ModelSerializer.to_internal_value',
       Mock(return_value={'a': 1, 'b': 2}))
def test_error():
    class TestSerializer(PermittedFieldsSerializerMixIn, ModelSerializer):
        class Meta:
            model = Mock()

        def has_field_permission(self, user, model, field):
            return field == 'a'

    serializer = TestSerializer(context={'request': Mock()})
    with pytest.raises(ValidationError):
        serializer.to_internal_value({'a': 1, 'b': 2})


@patch('rest_framework.serializers.ModelSerializer.to_internal_value',
       Mock(return_value={'a': 1, 'b': 2}))
def test_success():
    class TestSerializer(PermittedFieldsSerializerMixIn, ModelSerializer):
        class Meta:
            model = Mock()

        def has_field_permission(self, user, model, field):
            return True

    serializer = TestSerializer(context={'request': Mock()})
    assert serializer.to_internal_value({'a': 1, 'b': 2}) == {'a': 1, 'b': 2}
