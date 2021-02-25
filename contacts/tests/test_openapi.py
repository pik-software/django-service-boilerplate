import pytest
from rest_framework import status

from contacts.models import Comment, Contact
from core.tests.utils import add_user_permissions


@pytest.fixture
def permitted_api_client(api_user, api_client):
    add_user_permissions(api_user, Comment, 'view')
    add_user_permissions(api_user, Contact, 'view')
    return api_client


def test_api_schema_unauthorized(anon_api_client):
    res = anon_api_client.get('/api/v1/schema/?format=openapi-json')
    assert res.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


def test_api_common_schema(permitted_api_client):
    res = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data['openapi'] == '3.0.2'
    assert data['info']['title'] == 'Сервис API'
    assert data['info']['description'] == ('Тестовый сервис. Предоставляет '
                                           'инструменты для управления '
                                           'контактами и комментариями.')


def test_api_schema(permitted_api_client):
    response = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert response.status_code == 200
    data = response.json()
    definitions = data['components']['schemas']
    assert 'Comment' in definitions
    assert 'Contact' in definitions
    assert '/api/v1/comment-list/' in data['paths']
    assert '/api/v1/comment-list/{_uid}/' in data['paths']
    assert '/api/v1/contact-list/' in data['paths']
    assert '/api/v1/contact-list/{_uid}/' in data['paths']


def test_api_contact_model_schema(permitted_api_client):
    response = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert response.status_code == 200
    data = response.json()
    contact = data['components']['schemas']['Contact']
    assert contact == {'properties': {
        '_uid': {'type': 'string', 'title': 'Uid', 'readOnly': True,
                 'format': 'uuid', 'description': 'Идентификатор Контакта'},
        '_type': {'type': 'string', 'title': 'Type', 'readOnly': True,
                  'enum': ['contact']},
        '_version': {'type': 'integer', 'title': 'Version', 'readOnly': True},
        'created': {'type': 'string', 'format': 'date-time', 'title': 'Создан',
                    'readOnly': True},
        'updated': {'type': 'string', 'format': 'date-time',
                    'title': 'Updated', 'readOnly': True},
        'name': {'type': 'string', 'title': 'Наименование', 'maxLength': 255},
        'phones': {'type': 'array', 'items': {
            'type': 'string', 'title': 'Phones'},
                   'title': 'Номера телефонов',
                   'description': 'Номера телефонов вводятся в произвольном '
                                  'формате через запятую'},
        'emails': {'type': 'array', 'items': {'format': 'email',
                                              'title': 'Emails',
                                              'type': 'string'},
                   'title': 'E-mail адреса',
                   'description': 'E-mail адреса вводятся через запятую'},
        'order_index': {'type': 'integer', 'maximum': 2147483647,
                        'minimum': -2147483648,
                        'title': 'Индекс для сортировки'},
        'category': {'anyOf': [{'$ref': '#/components/schemas/Category'}],
                     'title': 'Категория',
                     'description': 'Категория контакта'},
        'contact_type': {'enum': [0, 1, 2, 3],
                         'maximum': 2147483647,
                         'minimum': -2147483648,
                         'title': 'Тип контакта',
                         'x-enumNames': ['Неизвестный', 'Сотрудник',
                                         'Подрядчик', 'Клиент']}},
        'required': ['name'], 'title': 'Контакт',
        'x-title-plural': 'Контакты', 'description': 'Модель контакта'}


def test_api_contact_list_schema(permitted_api_client):
    response = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert response.status_code == 200
    data = response.json()
    comment_list = (
        data['paths']['/api/v1/contact-list/']['get']['responses']['200']
        ['content']['application/json']['schema'])
    assert comment_list == {'type': 'object', 'properties': {
        'count': {'type': 'integer', 'example': 123},
        'page': {'type': 'integer'}, 'page_size': {'type': 'integer'},
        'pages': {'type': 'integer'},
        'page_next': {'type': 'integer', 'nullable': True},
        'page_previous': {'type': 'integer', 'nullable': True},
        'results': {'type': 'array', 'items': {
            'anyOf': [{'$ref': '#/components/schemas/Contact'}],
            'title': 'Контакт', 'description': 'Модель контакта'}}}}


def test_api_comment_model_schema(permitted_api_client):
    response = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert response.status_code == 200
    data = response.json()
    comment = data['components']['schemas']['Comment']
    assert comment == {
        'properties': {
            '_uid': {'type': 'string', 'title': 'Uid', 'readOnly': True,
                     'format': 'uuid',
                     'description': 'Идентификатор Комментария'},
            '_type': {'type': 'string', 'title': 'Type', 'readOnly': True,
                      'enum': ['comment']},
            '_version': {'type': 'integer', 'title': 'Version',
                         'readOnly': True},
            'created': {'type': 'string', 'format': 'date-time',
                        'title': 'Создан',
                        'readOnly': True},
            'updated': {'type': 'string', 'format': 'date-time',
                        'title': 'Updated', 'readOnly': True},
            'user': {'type': 'integer', 'title': 'User'},
            'contact': {'anyOf': [{'$ref': '#/components/schemas/Contact'}],
                        'title': 'Contact', 'description': ''},
            'message': {'type': 'string', 'title': 'Сообщение'}},
        'required': ['contact', 'message'],
        'title': 'Коментарий', 'x-title-plural': 'Коментарии',
        'description': 'Модель комментария'}


def test_api_comment_list_schema(permitted_api_client):
    response = permitted_api_client.get(f'/api/v1/schema/?format=openapi-json')
    assert response.status_code == 200
    data = response.json()
    comment_list = (
        data['paths']['/api/v1/comment-list/']['get']['responses']['200']
        ['content']['application/json']['schema'])
    assert comment_list == {
        'type': 'object',
        'properties': {
            'count': {'type': 'integer', 'example': 123},
            'page': {'type': 'integer'},
            'page_size': {'type': 'integer'},
            'pages': {'type': 'integer'},
            'page_next': {'type': 'integer',
                          'nullable': True},
            'page_previous': {'type': 'integer',
                              'nullable': True},
            'results': {'type': 'array', 'items': {
                'anyOf': [{
                    '$ref': '#/components/schemas/Comment'}],
                'description': 'Модель комментария',
                'title': 'Коментарий'}}}}
