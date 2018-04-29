import pytest
import unittest.mock as mock
from tempfile import TemporaryFile

import django.test
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from rest_framework import status

from core.tests.fixtures import create_user


url = '/api/target-data-importer/'


@pytest.fixture
def logged_user_client(client: django.test.Client):
    user = create_user()
    client.force_login(user)
    return client


@pytest.fixture
def logged_user_client_with_permission(client: django.test.Client):
    user = create_user()
    content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.create(
        codename='can_post_api_import',
        name='Может загружать данные по API.',
        content_type=content_type,
    )
    permission.save()
    user.user_permissions.add(permission)
    user.save()
    client.force_login(user)
    return client


@pytest.fixture()
def file():
    file_ = TemporaryFile()
    file_.write(b'Test string\n')
    file_.seek(0)
    yield file_
    file_.close()


def test_unauthorised(client: django.test.Client):
    res = client.post(url)
    assert status.HTTP_401_UNAUTHORIZED == res.status_code


def test_authorised_without_permission(logged_user_client):
    res = logged_user_client.post(url)
    assert status.HTTP_403_FORBIDDEN == res.status_code


def test_with_permission_and_no_file(logged_user_client_with_permission):
    res = logged_user_client_with_permission.post(url)
    assert status.HTTP_400_BAD_REQUEST == res.status_code


@mock.patch('core.views.target_api_import.default_storage.save')
def test_with_permission_and_file(storage_mock,
                                  logged_user_client_with_permission,
                                  file):
    res = logged_user_client_with_permission.post(url, data={'data.txt': file})
    assert status.HTTP_200_OK == res.status_code
    storage_mock.assert_called_once()
