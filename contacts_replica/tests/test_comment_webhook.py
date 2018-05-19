# pylint: disable=invalid-name
from copy import deepcopy

import pytest
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient

from contacts_replica.models import CommentReplica
from contacts_replica.tests.factories import ContactReplicaFactory
from core.tasks.fixtures import create_user

UID = '98cf09b3-cc36-4818-a6a2-417843c8f164'
USER_PK = 99999
CONTACT_UID = "c05bfac5-7c20-4754-aacb-a703a7e595c4"
WEBHOOK_DATA = {
    "count": 1, "pages": 1, "page_size": 20, "page": 1, "page_next": None,
    "page_previous": None, "results": [{
        "history_id": 133, "history_date": "2018-04-30T12:04:33.690145",
        "history_change_reason": None, "history_user_id": None,
        "history_type": "+", "_uid": UID, "_type": "comment", "_version": 1,
        "user": USER_PK, "contact": {
            "_uid": CONTACT_UID, "_type": "contact", "_version": 1,
            "name": "Mario Green", "phones": ["3728"],
            "emails": ["mario green@example.com"], "order_index": 100},
        "message": "Main type individual manage bag inside nothing."}]}


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


def _get_webhook_data(user=None):
    data = deepcopy(WEBHOOK_DATA)
    if user:
        data['results'][0]['user'] = user.pk
    return data


def test_receive_webhook_without_user(api_client: APIClient):
    data = _get_webhook_data()
    ContactReplicaFactory.create(uid=CONTACT_UID)
    r = api_client.post(f'/api/v1/webhook/', data=data)
    print(r.json())
    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json() == {
        'code': 'webhook_processing_error',
        'message': 'WEBHOOK: comment.+.98cf09b3-cc36-4818-a6a2-'
                   '417843c8f164: FK "user": DoesNotExists (v=1)'}


def test_receive_webhook_without_contact(api_client: APIClient):
    data = _get_webhook_data(api_client.user)
    r = api_client.post(f'/api/v1/webhook/', data=data)
    print(r.json())
    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json() == {
        'code': 'webhook_processing_error',
        'message': 'WEBHOOK: comment.+.98cf09b3-cc36-4818-a6a2-'
                   '417843c8f164: FK "contact": DoesNotExists (v=1)'}


def test_receive_webhook(api_client: APIClient):
    pyload = _get_webhook_data(api_client.user)
    ContactReplicaFactory.create(uid=CONTACT_UID)
    r = api_client.post(f'/api/v1/webhook/', data=pyload)
    print(r.json())
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {'status': 'ok'}


def test_receive_webhook_more_then_one_time(api_client: APIClient):
    data = _get_webhook_data(api_client.user)
    ContactReplicaFactory.create(uid=CONTACT_UID)
    r = api_client.post(f'/api/v1/webhook/', data=data)
    assert r.status_code == 200
    r = api_client.post(f'/api/v1/webhook/', data=data)
    assert r.status_code == 200
    r = api_client.post(f'/api/v1/webhook/', data=data)
    assert r.status_code == 200

    last = CommentReplica.objects.last()
    assert str(last.uid) == UID
    assert last.version == 1
