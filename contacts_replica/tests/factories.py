import random

import factory
import factory.fuzzy

from core.tasks.fixtures import create_user
from ..models import ContactReplica, CommentReplica


def _get_random_internal_phones():
    return [str(random.randint(1000, 9999))]


def _get_random_external_phones():
    count = random.randint(1, 5)
    return [
        "+{}".format(random.randint(79068077767, 99968077767))
        for _ in range(count)]


class ContactReplicaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactReplica

    name = factory.Faker('name')
    phones = factory.LazyAttribute(
        lambda x: _get_random_internal_phones())
    emails = factory.LazyAttribute(
        lambda x: ['{0}@example.com'.format(x.name).lower()])


class CommentReplicaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentReplica

    contact = factory.SubFactory(ContactReplicaFactory)
    message = factory.Faker('text')
    user = factory.LazyAttribute(
        lambda x: create_user())
