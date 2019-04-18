import random

import factory
import factory.fuzzy

from core.tasks.fixtures import create_user
from ..models import Contact, Comment, Category


def _get_random_internal_phones():
    return [str(random.randint(1000, 9999))]


def _get_random_external_phones():
    count = random.randint(1, 5)
    return [
        "+{}".format(random.randint(79068077767, 99968077767))
        for _ in range(count)]


def _gen_if_probability(model_factory, probability, **kwargs):
    assert 0 < probability < 100
    number = random.randint(0, 100)
    if number < probability:
        return model_factory.create(**kwargs)
    return None


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('name')
    parent = factory.LazyAttribute(
        lambda x: _gen_if_probability(CategoryFactory, 40, parent=x))  # noqa: pylint=undefined-variable


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    name = factory.Faker('name')
    phones = factory.LazyAttribute(
        lambda x: _get_random_internal_phones())
    emails = factory.LazyAttribute(
        lambda x: ['{0}@example.com'.format(x.name).lower()])
    category = factory.LazyAttribute(
        lambda x: _gen_if_probability(CategoryFactory, 20, parent=x))


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    contact = factory.SubFactory(ContactFactory)
    message = factory.Faker('text')
    user = factory.LazyAttribute(
        lambda x: create_user())
