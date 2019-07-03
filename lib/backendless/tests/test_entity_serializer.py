from copy import deepcopy

from pytest import raises
from rest_framework.exceptions import ValidationError

from ..models import DEFAULT_SCHEMA, Entity
from ..api import EntitySerializer
from .factories import EntityFactory


def test_retrieve_protocol():
    instance = EntityFactory.create()
    serializer = EntitySerializer(instance)
    assert serializer.data == {
        '_uid': instance.pk,
        '_type': instance.type.slug,
        '_version': instance.version,
        'created': instance.created,
        'updated': instance.updated,
        'foo': 1,
        'bar': instance.value['bar'],
    }


def test_list_protocol():
    instance = EntityFactory.create()
    serializer = EntitySerializer([instance, instance], many=True)
    res = {
        '_uid': instance.pk,
        '_type': instance.type.slug,
        '_version': instance.version,
        'created': instance.created,
        'updated': instance.updated,
        'foo': 1,
        'bar': instance.value['bar'],
    }
    assert serializer.data == [res, res]


def test_serializer_schema_support():
    instance = EntityFactory.create()
    schema = deepcopy(DEFAULT_SCHEMA)
    schema['properties']['bar'] = {'type': 'integer'}
    serializer = EntitySerializer(instance, context={'schema': schema})
    # no foo key here!
    assert serializer.data == {
        '_uid': instance.pk,
        '_type': instance.type.slug,
        '_version': instance.version,
        'created': instance.created,
        'updated': instance.updated,
        'bar': instance.value['bar'],
    }


def test_create_protocol_no_foo():
    obj = EntityFactory.create()
    serializer = EntitySerializer(data={}, context={'type': obj.type})
    with raises(ValidationError):
        serializer.is_valid(raise_exception=True)


def test_create_protocol():
    obj = EntityFactory.create()
    count0 = Entity.objects.count()
    serializer = EntitySerializer(data={'foo': 3}, context={'type': obj.type})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert Entity.objects.count() == count0 + 1
    assert Entity.objects.first().value['foo'] == 3


def test_partial_support():
    obj = EntityFactory.create()
    serializer = EntitySerializer(
        data={}, context={'type': obj.type}, partial=True)
    assert serializer.is_valid(raise_exception=True)


def test_update_protocol():
    obj = EntityFactory.create()
    count0 = Entity.objects.count()
    serializer = EntitySerializer(obj, data={'foo': 3, 'nonfoo': 10, 'bar': 0},
                                  context={'type': obj.type}, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert Entity.objects.count() == count0
    assert Entity.objects.first().value == {'bar': 0, 'foo': 3}


def test_update_protocol_not_change_existing_value():
    obj = EntityFactory.create()
    count0 = Entity.objects.count()
    assert obj.value['bar'] > 0
    serializer = EntitySerializer(obj, data={'foo': 3},
                                  context={'type': obj.type}, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert Entity.objects.count() == count0
    assert Entity.objects.first().value == {'bar': obj.value['bar'], 'foo': 3}
