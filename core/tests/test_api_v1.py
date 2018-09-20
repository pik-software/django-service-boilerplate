import pytest
import django.test
from pik.core.tests import create_user
from rest_framework import status


@pytest.fixture
def logged_user_client(client: django.test.Client):
    user = create_user()
    user.save()
    client.force_login(user)
    client.user = user
    return client


def test_smoke_schema(logged_user_client):
    res = logged_user_client.get('/api/v1/schema/')
    assert res.status_code == status.HTTP_200_OK
