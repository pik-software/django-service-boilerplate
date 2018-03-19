import pytest

from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


@pytest.fixture(params=[
    (Contact, ContactFactory),
    (Comment, CommentFactory),
])
def model_and_factory(request):
    return request.param


@pytest.fixture(params=[
    (Contact, ContactFactory),
    (Comment, CommentFactory),
])
def critical_model_and_factory(request):
    return request.param


def test_create_model_by_factories(model_and_factory):  # noqa: pylint=redefined-outer-name
    model, factory = model_and_factory
    obj1 = factory.create()
    obj2 = model.objects.last()
    if hasattr(obj1, 'uid'):
        assert obj1.uid == obj2.uid
    if hasattr(obj1, 'id'):
        assert obj1.id == obj2.id
    assert obj1.pk == obj2.pk
    assert str(obj1) == str(obj2)


def test_critical_model_protocol(critical_model_and_factory):  # noqa: pylint=redefined-outer-name
    model, factory = critical_model_and_factory  # noqa: pylint=unused-variable
    fields = [f.name for f in model._meta.get_fields()]  # noqa: pylint=protected-access
    assert hasattr(model, 'history')
    assert model.UID_PREFIX != 'OBJ'
    assert 'uid' in fields
    assert 'version' in fields
    assert 'created' in fields
    assert 'updated' in fields
    assert hasattr(model._meta, 'verbose_name')  # noqa
    assert hasattr(model._meta, 'verbose_name_plural')  # noqa
    assert '__str__' in model.__dict__.keys()  # noqa
