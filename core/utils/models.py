from typing import Optional, List

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model, Manager, Field


def has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)  # noqa
        return True
    except FieldDoesNotExist:
        return False


def get_fields(model) -> List[Field]:
    return model._meta.get_fields()  # noqa


def get_pk_name(model) -> Optional[str]:
    fields = get_fields(model)
    for field in fields:
        if field.primary_key:
            return field.name
    return None


def get_model(app_label: str, model_name: str) -> Model:
    return apps.get_model(app_label, model_name)


def get_base_manager(model) -> Manager:
    return model._base_manager  # noqa
