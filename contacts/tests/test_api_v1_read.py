from pprint import pprint

from rest_framework import status

from core.tests.utils import add_user_permissions
from ..models import Contact, Comment
from ..tests.factories import ContactFactory, CommentFactory


def _assert_api_object_list(res, result):
    data = res.json()['results']
    pprint(data)
    assert data == result


def _assert_api_object(res, result):
    data = res.json()
    pprint(data)
    assert data == result


def test_api_list_contact(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Contact, 'view')
    obj = ContactFactory.create()
    res = api_client.get('/api/v1/contact-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [
        {
            '_uid': str(obj.uid),
            '_type': 'contact',
            '_version': obj.version,
            'contact_type': 0,
            'created': obj.created.isoformat(),
            'updated': obj.updated.isoformat(),
            'emails': obj.emails,
            'name': obj.name,
            'phones': obj.phones,
            'order_index': obj.order_index,
            'category': {'_uid': str(obj.category.uid),
                         '_type': 'category', '_version': 1,
                         'created': obj.category.created.isoformat(),
                         'updated': obj.category.updated.isoformat(),
                         'name': obj.category.name, 'parent': None}
        }
    ])


def test_api_retrieve_contact(api_user, api_client):
    add_user_permissions(api_user, Contact, 'view')
    obj = ContactFactory.create()
    res = api_client.get(f'/api/v1/contact-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res, {
        '_uid': str(obj.uid),
        '_type': 'contact',
        '_version': obj.version,
        'contact_type': 0,
        'created': obj.created.isoformat(),
        'updated': obj.updated.isoformat(),
        'emails': obj.emails,
        'name': obj.name,
        'phones': obj.phones,
        'order_index': obj.order_index,
        'category': {'_uid': str(obj.category.uid),
                     '_type': 'category', '_version': 1,
                     'created': obj.category.created.isoformat(),
                     'updated': obj.category.updated.isoformat(),
                     'name': obj.category.name, 'parent': None}
    })


def test_api_contact_history(api_user, api_client):
    obj = ContactFactory.create()
    hist_obj = obj.history.last()
    add_user_permissions(api_user, Contact.history.model, 'view')
    res = api_client.get(f'/api/v1/contact-list/history/?_uid={obj.uid}')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [{
        '_uid': str(obj.uid),
        '_type': 'historical' + 'contact',
        '_version': obj.version,
        'created': obj.created.isoformat(),
        'updated': obj.updated.isoformat(),
        'emails': obj.emails,
        'name': obj.name,
        'order_index': obj.order_index,
        'phones': obj.phones,
        'contact_type': 0,
        'category': {'_uid': str(obj.category.uid),
                     '_type': 'category'},
        'history_change_reason': None,
        'history_date': hist_obj.history_date.isoformat(),
        'history_id': hist_obj.history_id,
        'history_type': '+',
        'history_user_id': None,
        'history_user': None,
    }])


def test_api_list_comment(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Comment, 'view')
    obj = CommentFactory.create()
    res = api_client.get('/api/v1/comment-list/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [
        {
            '_uid': str(obj.uid),
            '_type': 'comment',
            '_version': obj.version,
            'created': obj.created.isoformat(),
            'updated': obj.updated.isoformat(),
            'contact': {
                '_uid': str(obj.contact.uid),
                '_type': 'contact',
                '_version': obj.contact.version,
                'contact_type': 0,
                'created': obj.contact.created.isoformat(),
                'updated': obj.contact.updated.isoformat(),
                'emails': obj.contact.emails,
                'name': obj.contact.name,
                'order_index': obj.contact.order_index,
                'phones': obj.contact.phones,
                'category': {
                    '_uid': str(obj.contact.category.uid),
                    '_type': 'category', '_version': 1,
                    'created': obj.contact.category.created.isoformat(),
                    'updated': obj.contact.category.updated.isoformat(),
                    'name': obj.contact.category.name, 'parent': None}
            },
            'message': obj.message,
            'user': obj.user.pk,
        }
    ])


def test_api_retrieve_comment(api_user, api_client):
    add_user_permissions(api_user, Comment, 'view')
    obj = CommentFactory.create()
    res = api_client.get(f'/api/v1/comment-list/{obj.uid}/')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object(res, {
        '_uid': str(obj.uid),
        '_type': 'comment',
        '_version': obj.version,
        'created': obj.created.isoformat(),
        'updated': obj.updated.isoformat(),
        'contact': {
            '_uid': str(obj.contact.uid),
            '_type': 'contact',
            '_version': obj.contact.version,
            'created': obj.contact.created.isoformat(),
            'updated': obj.contact.updated.isoformat(),
            'emails': obj.contact.emails,
            'name': obj.contact.name,
            'order_index': obj.contact.order_index,
            'phones': obj.contact.phones,
            'contact_type': 0,
            'category': {
                '_uid': str(obj.contact.category.uid),
                '_type': 'category', '_version': 1,
                'created': obj.contact.category.created.isoformat(),
                'updated': obj.contact.category.updated.isoformat(),
                'name': obj.contact.category.name, 'parent': None}
        },
        'message': obj.message,
        'user': obj.user.pk,
    })


def test_api_comment_history(api_user, api_client):
    obj = CommentFactory.create()
    hist_obj = obj.history.last()
    add_user_permissions(api_user, Comment.history.model, 'view')
    res = api_client.get(f'/api/v1/comment-list/history/?_uid={obj.uid}')
    assert res.status_code == status.HTTP_200_OK
    _assert_api_object_list(res, [{
        '_uid': str(obj.uid),
        '_type': 'historical' + 'comment',
        '_version': obj.version,
        'created': obj.created.isoformat(),
        'updated': obj.updated.isoformat(),
        'contact': {
            '_uid': str(obj.contact.uid),
            '_type': 'contact'},
        'message': obj.message,
        'user': obj.user.pk,
        'history_change_reason': None,
        'history_date': hist_obj.history_date.isoformat(),
        'history_id': hist_obj.history_id,
        'history_type': '+',
        'history_user_id': None,
        'history_user': None}])
