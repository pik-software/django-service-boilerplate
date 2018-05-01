import pytest

from eventsourcing.replicated.registry import is_replicated
from ..models import ContactReplica, CommentReplica
from ..tests.factories import ContactReplicaFactory, \
    CommentReplicaFactory


@pytest.fixture(params=[
    (ContactReplica, ContactReplicaFactory),
    (CommentReplica, CommentReplicaFactory),
])
def model_and_factory(request):
    return request.param


def test_model_already_registered(model_and_factory):
    model, _ = model_and_factory
    assert is_replicated(model)
