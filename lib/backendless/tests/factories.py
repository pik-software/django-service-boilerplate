import random

import factory.fuzzy

from ..models import EntityType, Entity


class EntityTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntityType

    name = factory.Faker('name')
    slug = factory.Faker('slug')
    schema = factory.LazyAttribute(
        lambda x: {
            'type': 'object',
            'required': ['foo'],
            'properties': {
                'foo': {'title': 'uid', 'type': 'integer'},
                'bar': {'title': 'uid', 'type': 'integer'},
            }
        }
    )


class EntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entity

    type = factory.SubFactory(EntityTypeFactory)
    value = factory.LazyAttribute(
        lambda x: {'foo': 1, 'bar': random.randint(100, 900)})
