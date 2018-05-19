# pylint: disable=protected-access
import pytest

from ..models import CommentReplica
from ..tests.factories import CommentReplicaFactory


@pytest.fixture(params=[
    (CommentReplica, CommentReplicaFactory, {'fk': 'contact'}),
])
def model_and_factory(request):
    return request.param


def test_soft_delete_parent_obj(model_and_factory):
    model, factory, options = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    parent = getattr(obj, options['fk'])
    parent.delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert model._base_manager.filter(pk=obj_pk).last()


def test_soft_delete_parent_qs(model_and_factory):
    model, factory, options = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    parent = getattr(obj, options['fk'])
    parent_pk = parent.pk
    type(parent).objects.filter(pk=parent_pk).delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert model._base_manager.filter(pk=obj_pk).last()


def test_hard_delete_parent_obj(model_and_factory):
    model, factory, options = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    parent = getattr(obj, options['fk'])
    parent.hard_delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert not model._base_manager.filter(pk=obj_pk).last()


def test_hard_delete_parent_qs(model_and_factory):
    model, factory, options = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    parent = getattr(obj, options['fk'])
    parent_pk = parent.pk
    type(parent).objects.filter(pk=parent_pk).hard_delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert not model._base_manager.filter(pk=obj_pk).last()
