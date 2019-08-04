from freezegun import freeze_time
from rest_framework import status

from core.tests.utils import add_user_permissions

from .factories import ContactFactory
from ..models import Contact


def test_api_filter_by_updated(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Contact, 'view')
    with freeze_time("2012-01-14"):
        ContactFactory.create()
        obj = ContactFactory.create()
    with freeze_time("2013-01-14"):
        ContactFactory.create()
        obj.name += '(new)'
        obj.save()
    ContactFactory.create()

    res = api_client.get('/api/v1/contact-list/')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 4

    filter_date = '2012-04-12T22:33:45.028342'
    res = api_client.get(f'/api/v1/contact-list/?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'/api/v1/contact-list/?updated__gte={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 3

    filter_date = '2013-01-14T00:00:00'
    res = api_client.get(f'/api/v1/contact-list/?updated__gt={filter_date}')
    assert res.status_code == status.HTTP_200_OK
    assert res.json()['count'] == 1
