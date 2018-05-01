import pytest

from eventsourcing.replicator import is_replicating
from ..models import Contact, Comment
from ..tests.factories import CommentFactory, ContactFactory


@pytest.fixture(params=[
    (Contact, ContactFactory),
    (Comment, CommentFactory),
])
def model_and_factory(request):
    return request.param


def test_model_already_registered(model_and_factory):
    model, _ = model_and_factory
    assert is_replicating(model)
