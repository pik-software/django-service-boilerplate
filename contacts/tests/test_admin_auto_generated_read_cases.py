import pytest
from django.urls import reverse
from rest_framework import status

from contacts.models import Contact
from contacts.tests.factories import ContactFactory
from core.tests.utils import add_admin_access_permission, add_permissions


@pytest.fixture(params=[
    (Contact, ContactFactory),
])
def admin_model(request):
    return request.param


def _get_admin_changelist_url(model):
    meta = model._meta  # noqa
    return reverse(f'admin:{meta.app_label}_{meta.model_name}_changelist')


def test_admin_index_access_denied(api_client):
    res = api_client.get(reverse('admin:index'))
    assert res.status_code == status.HTTP_302_FOUND


def test_admin_index(api_user, api_client):
    add_admin_access_permission(api_user)
    res = api_client.get(reverse('admin:index'))
    assert res.status_code == status.HTTP_200_OK


def test_admin_model_access_denied(api_user, api_client, admin_model):
    model, _ = admin_model
    add_admin_access_permission(api_user)
    res = api_client.get(_get_admin_changelist_url(model))
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_admin_model(api_user, api_client, admin_model):
    model, _ = admin_model
    add_admin_access_permission(api_user)
    add_permissions(api_user, model, 'view')
    res = api_client.get(_get_admin_changelist_url(model))
    assert res.status_code == status.HTTP_200_OK
