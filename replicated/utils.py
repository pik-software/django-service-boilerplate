from django.core.exceptions import FieldDoesNotExist


def _has_field(model, field):
    try:
        model._meta.get_field(field)  # noqa
        return True
    except FieldDoesNotExist:
        return False


def _get_fields(model):
    return model._meta.get_fields()  # noqa
