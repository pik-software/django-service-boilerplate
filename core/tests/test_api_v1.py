import pytest
from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.auth import get_user_model
from django.test import override_settings

from core.tests.utils import create_permission as create_perm
from core.utils.permissions import (
    get_permissions_from_allowed_apps, NotAllowedUserTypeError)


BASE_API_URL = '/api/v1/'
SCHEMA_API_URL = BASE_API_URL + 'schema/?format=openapi-json'
PERMISSIONS_API_URL = BASE_API_URL + 'permissions/'


def test_smoke_schema(api_client):
    res = api_client.get(SCHEMA_API_URL)
    assert res.status_code == 200


class TestPermissions:

    @staticmethod
    def _get_sorted_perm_names(perm_names):
        return sorted(perm_names, key=lambda d: d['code_name'])

    def _get_all_expected_perm_names(self, granted=False):
        expected_perm_names = [
            {'code_name': 'add_group',
             'verbose_name': 'Can add group', 'granted': granted},
            {'code_name': 'change_group',
             'verbose_name': 'Can change group', 'granted': granted},
            {'code_name': 'delete_group',
             'verbose_name': 'Can delete group', 'granted': granted},
            {'code_name': 'view_group',
             'verbose_name': 'Can view group', 'granted': granted},
            {'code_name': 'add_permission',
             'verbose_name': 'Can add permission', 'granted': granted},
            {'code_name': 'change_permission',
             'verbose_name': 'Can change permission', 'granted': granted},
            {'code_name': 'delete_permission',
             'verbose_name': 'Can delete permission', 'granted': granted},
            {'code_name': 'view_permission',
             'verbose_name': 'Can view permission', 'granted': granted},
            {'code_name': 'add_user',
             'verbose_name': 'Can add user', 'granted': granted},
            {'code_name': 'change_user',
             'verbose_name': 'Can change user', 'granted': granted},
            {'code_name': 'delete_user',
             'verbose_name': 'Can delete user', 'granted': granted},
            {'code_name': 'view_user',
             'verbose_name': 'Can view user', 'granted': granted}]

        return expected_perm_names

    def test_anonymous_user_get_permissions(self, anon_api_client):
        response = anon_api_client.get(PERMISSIONS_API_URL)

        assert response.status_code == 403

    @override_settings(ALLOWED_APPS_FOR_PERMISSIONS_VIEW={})
    def test_get_permissions_without_allowed_apps(self, api_client):
        response = api_client.get(PERMISSIONS_API_URL)

        assert response.status_code == 200
        assert response.json()['permissions'] == []

    @override_settings(ALLOWED_APPS_FOR_PERMISSIONS_VIEW={'auth'})
    def test_authenticated_user_get_user_permissions(self, api_client):
        perm_name = 'perm_name'
        perm_codename = 'perm_codename'
        user = get_user_model().objects.get()
        perm = create_perm(user._meta.model_name, perm_name, perm_codename) # noqa: protected-access
        user.user_permissions.add(perm)
        granted_perm_names = {
            'verbose_name': perm_name,
            'code_name': perm_codename,
            'granted': True
        }
        expected_perms = self._get_all_expected_perm_names()
        expected_perms.append(granted_perm_names)

        response = api_client.get(PERMISSIONS_API_URL)

        assert response.status_code == 200
        result_perms = response.json()['permissions']
        assert self._get_sorted_perm_names(
            result_perms) == self._get_sorted_perm_names(expected_perms)

    @override_settings(ALLOWED_APPS_FOR_PERMISSIONS_VIEW={'auth'})
    def test_authenticated_user_get_group_permissions(self, api_client):
        perm_name = 'perm_name'
        perm_codename = 'perm_codename'
        user = get_user_model().objects.get()
        perm_group = Group.objects.create(name='group_name')
        perm = create_perm(user._meta.model_name, perm_name, perm_codename) # noqa: protected-access
        perm_group.permissions.add(perm)
        perm_group.user_set.add(user)
        granted_perm_names = {
            'verbose_name': perm_name,
            'code_name': perm_codename,
            'granted': True
        }
        expected_perms = self._get_all_expected_perm_names()
        expected_perms.append(granted_perm_names)

        response = api_client.get(PERMISSIONS_API_URL)

        assert response.status_code == 200
        result_perms = response.json()['permissions']
        assert self._get_sorted_perm_names(
            result_perms) == self._get_sorted_perm_names(expected_perms)

    @override_settings(ALLOWED_APPS_FOR_PERMISSIONS_VIEW={'auth'})
    def test_superuser_get_permissions(self, api_client):
        user_model = get_user_model()
        user = user_model.objects.get()
        user.is_superuser = True
        user.save()
        expected_perm_names = self._get_all_expected_perm_names(granted=True)

        response = api_client.get(PERMISSIONS_API_URL)

        assert response.status_code == 200
        result_perms = response.json()['permissions']
        assert self._get_sorted_perm_names(
            result_perms) == self._get_sorted_perm_names(expected_perm_names)

    def test_get_permissions_from_allowed_apps(self, api_user):
        api_user.is_active = False
        api_user.save()
        with pytest.raises(NotAllowedUserTypeError):
            get_permissions_from_allowed_apps(api_user, {})

        with pytest.raises(NotAllowedUserTypeError):
            get_permissions_from_allowed_apps(AnonymousUser(), {})
