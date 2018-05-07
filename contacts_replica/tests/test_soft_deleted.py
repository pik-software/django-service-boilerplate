import pytest

from ..models import ContactReplica, CommentReplica
from ..tests.factories import ContactReplicaFactory, \
    CommentReplicaFactory


@pytest.fixture(params=[
    (ContactReplica, ContactReplicaFactory),
    (CommentReplica, CommentReplicaFactory),
])
def model_and_factory(request):
    return request.param


def test_soft_delete_obj(model_and_factory):
    model, factory = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    obj.delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert model._base_manager.filter(pk=obj_pk).last()


def test_soft_delete_qs(model_and_factory):
    model, factory = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    model.objects.filter(pk=obj_pk).delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert model._base_manager.filter(pk=obj_pk).last()


def test_hard_delete_obj(model_and_factory):
    model, factory = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    obj.hard_delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert not model._base_manager.filter(pk=obj_pk).last()


def test_hard_delete_qs(model_and_factory):
    model, factory = model_and_factory
    obj = factory.create()
    obj_pk = obj.pk

    model.objects.filter(pk=obj_pk).hard_delete()

    assert not model.objects.filter(pk=obj_pk).last()
    assert not model._default_manager.filter(pk=obj_pk).last()
    assert not model._base_manager.filter(pk=obj_pk).last()
