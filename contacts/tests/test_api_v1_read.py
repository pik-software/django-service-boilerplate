from pprint import pprint

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from ..models import Contact
from ..tests.factories import ContactFactory


@pytest.fixture
def api_client():
    user = create_user()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


def _assert_api_results(data, result):
    data = list(map(dict, data['results']))
    pprint(data)
    assert data == result


def _assert_api_object(data, result):
    pprint(data)
    assert data == result


def test_api_list_contact(api_client):  # noqa: pylint=invalid-name
    obj = ContactFactory.create()
    res = api_client.get('/api/v1/contact-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_results(res.data, [
        {
            '_type': 'contact',
            '_uid': obj.uid,
            'emails': obj.emails,
            'name': obj.name,
            'order_index': obj.order_index,
            'phones': obj.phones,
        }
    ])


def test_api_retrieve_contact(api_client):
    obj = ContactFactory.create()
    res = api_client.get(f'/api/v1/contact-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res.data, {
        '_type': 'contact',
        '_uid': obj.uid,
        'emails': obj.emails,
        'name': obj.name,
        'order_index': obj.order_index,
        'phones': obj.phones,
    })
