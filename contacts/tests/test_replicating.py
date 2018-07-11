import pytest
from django.contrib.contenttypes.models import ContentType

from eventsourcing.replicator import is_replicating, get_replicating_model, \
    get_all_replicating_models
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


def test_get_replicating_model(model_and_factory):
    model, _ = model_and_factory
    _type = ContentType.objects.get_for_model(model).model
    assert get_replicating_model(_type) == model.history.model


def test_get_all_replicating_models(model_and_factory):
    model, _ = model_and_factory
    _type = ContentType.objects.get_for_model(model).model
    assert dict(get_all_replicating_models())[_type] == model.history.model
