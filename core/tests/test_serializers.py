from unittest.mock import Mock

import pytest

from core.api.serializers import StandardizedModelSerializer


@pytest.fixture
def model_class():
    field = Mock('field', verbose_name='field_label',
                 help_text='field_help')
    _meta = Mock(verbose_name='model_label',
                 verbose_name_plural='model_plural',
                 get_field=Mock('get_field', return_value=field))
    return Mock('Model', _meta=_meta, help_text='model_help')


@pytest.fixture
def serializer_class(model_class):
    class Serializer(StandardizedModelSerializer):
        class Meta:
            model = model_class
    return Serializer


def test_root_serializer_default_labels(model_class, serializer_class):
    serializer = serializer_class()
    assert serializer.label == 'model_label'
    assert serializer.label_plural == 'model_plural'
    assert serializer.help_text == 'model_help'


def test_root_serializer_set_labels(model_class, serializer_class):
    serializer = serializer_class(
        label='custom_label', help_text='custom_help',
        label_plural='custom_plural')
    assert serializer.label == 'custom_label'
    assert serializer.label_plural == 'custom_plural'
    assert serializer.help_text == 'custom_help'


def test_nested_serializer_default_labels(model_class, serializer_class):
    serializer = serializer_class()
    parent = serializer_class()
    serializer.bind('field_name', parent)
    assert serializer.label == 'field_label'
    assert serializer.label_plural == 'model_plural'
    assert serializer.help_text == 'field_help'


def test_nested_serializer_set_labels(model_class, serializer_class):
    serializer = serializer_class(
        label='custom_label', help_text='custom_help',
        label_plural='custom_plural')
    parent = serializer_class()
    serializer.bind('field_name', parent)
    assert serializer.label == 'custom_label'
    assert serializer.label_plural == 'custom_plural'
    assert serializer.help_text == 'custom_help'
