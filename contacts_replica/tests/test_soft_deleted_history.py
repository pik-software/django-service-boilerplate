# pylint: disable=protected-access
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


def _assert_history_object(hist_obj, type_, event_, uid_):
    _type = hist_obj.history_object._meta.model_name
    _event = hist_obj.history_type
    _uid = hist_obj.history_object.uid
    assert _type == type_
    assert _event == event_
    assert _uid == uid_


def test_soft_delete_obj(model_and_factory):
    model, factory = model_and_factory
    obj = factory.create()
    hist = obj.history.all()

    obj.delete()

    assert hist.count() == 2
    _assert_history_object(hist[0], model._meta.model_name, '-', obj.uid)
    _assert_history_object(hist[1], model._meta.model_name, '+', obj.uid)
