# pylint: disable=invalid-name
import pytest
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from contacts_replica.models import ContactReplica
from core.tasks.fixtures import create_user

UID = "f43c59ca-f632-4ada-98eb-99508fcfa072"
WEBHOOK_DATA = {
    "count": 1, "pages": 1, "page_size": 20, "page": 1, "page_next": None,
    "page_previous": None, "results": [
        {"_version": 1, "history_date": "2018-04-29T21:29:28.327108",
         "history_id": 128, "history_change_reason": None,
         "history_user_id": None, "history_type": "+", "_uid": UID,
         "_type": "contact", "name": "Erin Griffith", "phones": ["7519"],
         "emails": ["erin griffith@example.com"], "order_index": 100}]}


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture
def api_client():
    password = get_random_string()
    user = create_user(password=password)
    client = APIClient()
    client.force_login(user)
    client.user = user
    client.password = password
    return client


def test_receive_webhook_data(api_client: APIClient):
    r = api_client.post(f'/api/v1/webhook/', data=WEBHOOK_DATA)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    last = ContactReplica.objects.last()
    assert str(last.uid) == UID


def test_receive_webhook_more_then_one_time(api_client: APIClient):
    r = api_client.post(f'/api/v1/webhook/', data=WEBHOOK_DATA)
    assert r.status_code == 200
    r = api_client.post(f'/api/v1/webhook/', data=WEBHOOK_DATA)
    assert r.status_code == 200
    r = api_client.post(f'/api/v1/webhook/', data=WEBHOOK_DATA)
    assert r.status_code == 200

    last = ContactReplica.objects.last()
    assert str(last.uid) == UID
    assert last.version == 1
