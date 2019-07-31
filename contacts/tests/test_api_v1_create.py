from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework import status

from core.tests.utils import add_user_permissions
from ..models import Contact, Comment
from .factories import ContactFactory


REQUIRED_FIELD_ERROR = {'message': 'Это поле обязательно.', 'code': 'required'}


def test_api_create_contact_by_anon(anon_api_client):  # noqa: pylint=invalid-name
    data = {'name': get_random_string()}
    res = anon_api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_contact_without_permission(api_client):  # noqa: pylint=invalid-name
    data = {'name': get_random_string()}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_contact_without_name(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Contact, 'add')
    data = {'noname': get_random_string()}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'code': 'invalid',
        'detail': {
            'name': [REQUIRED_FIELD_ERROR]},
        'message': 'Invalid input.'}


def test_api_create_contact_with_extra_field(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Contact, 'add', 'change')
    data = {'name': get_random_string(), 'fooo': 'no'}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_create_contact(api_user, api_client):
    add_user_permissions(api_user, Contact, 'add', 'change')
    data = {'name': get_random_string()}
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED


def test_api_create_bulk_contact(api_user, api_client):
    add_user_permissions(api_user, Contact, 'add', 'change')
    data = [{'name': get_random_string()}, {'name': get_random_string()}]
    res = api_client.post('/api/v1/contact-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2


def test_api_create_comment_by_anon(anon_api_client):  # noqa: pylint=invalid-name
    data = {'message': get_random_string()}
    res = anon_api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_comment_without_permission(api_client):
    link = {'_uid': ContactFactory.create().uid, '_type': 'contact'}
    data = {'message': get_random_string(), 'contact': link}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_create_comment_without_contact(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Comment, 'add')
    data = {'message': get_random_string()}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data == {
        'message': 'Invalid input.', 'code': 'invalid',
        'detail': {
            'contact': [REQUIRED_FIELD_ERROR],
        }
    }


def test_api_create_comment(api_user, api_client):
    contact = ContactFactory.create()
    add_user_permissions(api_user, Comment, 'add', 'change')
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
        'name': get_random_string(),
    }
    data = {'message': get_random_string(), 'contact': payload}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data['user'] == api_user.pk


def test_api_create_comment_simple(api_user, api_client):
    contact = ContactFactory.create(name=api_user.username)
    add_user_permissions(api_user, Comment, 'add', 'change')
    data = {'message': get_random_string(), 'contact': contact.uid}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data['user'] == api_user.pk


def test_api_create_comment_otheruser(api_user, api_client):
    other_user = get_user_model().objects.create(username='other')
    contact = ContactFactory.create(name=api_user.username)
    add_user_permissions(api_user, Comment, 'add', 'change', 'change_user')
    data = {'message': get_random_string(), 'contact': contact.uid,
            'user': other_user.pk}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data['user'] == other_user.pk


def test_api_create_comment_otheruser_permitted(api_user, api_client):
    other_user = get_user_model().objects.create(username='other')
    contact = ContactFactory.create(name=api_user.username)
    add_user_permissions(api_user, Comment, 'add', 'change')
    data = {'message': get_random_string(), 'contact': contact.uid,
            'user': other_user.pk}
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == {
        'code': 'invalid',
        'detail': {'user_id': [{
            'code': 'invalid',
            'message': 'У вас нет прав для редактирования этого поля.'}]},
        'message': 'Invalid input.'}


def test_api_create_2_comments_for_one_contact(api_user, api_client):  # noqa: pylint=invalid-name
    add_user_permissions(api_user, Comment, 'add', 'change')
    contact = ContactFactory.create()
    payload = {
        '_uid': contact.uid,
        '_type': ContentType.objects.get_for_model(type(contact)).model,
    }

    data = [
        {'message': get_random_string(), 'contact': payload},
        {'message': get_random_string(), 'contact': payload}, ]
    res = api_client.post('/api/v1/comment-list/', data=data)
    assert res.status_code == status.HTTP_201_CREATED
    assert len(res.data) == 2
    assert contact.comments.all().count() == 2
