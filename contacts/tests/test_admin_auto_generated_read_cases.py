import pytest
from django.urls import reverse
from rest_framework import status

from contacts.models import Contact
from contacts.tests.factories import ContactFactory
from core.tests.utils import add_admin_access_permission, add_permissions


BATCH_MODELS = 5


@pytest.fixture(params=[
    (Contact, ContactFactory, {}),
])
def admin_model(request):
    return request.param


def _get_admin_changelist_url(model):
    meta = model._meta  # noqa
    return reverse(f'admin:{meta.app_label}_{meta.model_name}_changelist')


def _get_admin_change_url(model, obj):
    meta = model._meta  # noqa
    return reverse(
        f'admin:{meta.app_label}_{meta.model_name}_change',
        kwargs={'object_id': obj.pk})


def _create_few_models(factory, **kwargs):
    factory.create_batch(BATCH_MODELS)
    last_obj = factory.create(**kwargs)
    return last_obj


def test_admin_index_access_denied(api_client):
    res = api_client.get(reverse('admin:index'))
    assert res.status_code == status.HTTP_302_FOUND


def test_admin_index(api_user, api_client):
    add_admin_access_permission(api_user)
    res = api_client.get(reverse('admin:index'))
    assert res.status_code == status.HTTP_200_OK


def test_admin_model_access_denied(api_user, api_client, admin_model):
    model, factory, obj_kwargs = admin_model
    _create_few_models(factory, **obj_kwargs)
    add_admin_access_permission(api_user)
    res = api_client.get(_get_admin_changelist_url(model))
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_model(api_user, api_client, admin_model):
    model, factory, obj_kwargs = admin_model
    _create_few_models(factory, **obj_kwargs)
    add_admin_access_permission(api_user)
    add_permissions(api_user, model, 'view')
    res = api_client.get(_get_admin_changelist_url(model))
    assert res.status_code == status.HTTP_200_OK


def test_admin_model_object_access_denied(api_user, api_client, admin_model):
    model, factory, obj_kwargs = admin_model
    obj = _create_few_models(factory, **obj_kwargs)
    add_admin_access_permission(api_user)
    res = api_client.get(_get_admin_change_url(model, obj))
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_model_object(api_user, api_client, admin_model):
    model, factory, obj_kwargs = admin_model
    obj = _create_few_models(factory, **obj_kwargs)
    add_admin_access_permission(api_user)
    add_permissions(api_user, model, 'change')
    res = api_client.get(_get_admin_change_url(model, obj))
    assert res.status_code == status.HTTP_200_OK
