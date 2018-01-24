import pytest

from contacts.models import Contact
from contacts.tests.factories import ContactFactory


@pytest.fixture(params=[
    (Contact, ContactFactory),
])
def model_and_factory(request):
    return request.param


@pytest.fixture(params=[
    (Contact, ContactFactory),
])
def critical_model_and_factory(request):
    return request.param


def test_create_model_by_factories(model_and_factory):
    model, factory = model_and_factory
    obj1 = factory.create()
    obj2 = model.objects.last()
    assert obj1.id == obj2.id
    assert str(obj1) == str(obj2)


def test_critical_model_protocol(critical_model_and_factory):
    model, factory = critical_model_and_factory
    fields = [f.name for f in model._meta.get_fields()]
    assert hasattr(model, 'history')
    assert model.UID_PREFIX != 'OBJ'
    assert 'uid' in fields
    assert 'version' in fields
    assert 'created' in fields
    assert 'updated' in fields
