import factory.fuzzy

from django.utils import timezone

from lib.integra.models import UpdateState


class UpdateStateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UpdateState

    key = factory.Faker('slug')
    updated = factory.fuzzy.FuzzyAttribute(timezone.now)
