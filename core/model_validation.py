from django.db import models


def validate_and_create(model, **kwargs):
    assert issubclass(model, models.Model)
    # TODO: write tests
    obj = model(**kwargs)
    obj.full_clean()
    obj.save()
    return obj


def validate_and_update(obj, **kwargs):
    assert isinstance(obj, models.Model)
    # TODO: write tests
    for key in kwargs:
        setattr(obj, key, kwargs[key])
    obj.full_clean()
    obj.save()
