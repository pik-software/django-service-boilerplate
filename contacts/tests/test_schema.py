from rest_framework import status


def test_api_schema_unauthorized(anon_api_client):
    res = anon_api_client.get('/api/v1/schema/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_common_schema(api_client):
    res = api_client.get(f'/api/v1/schema/?format=openapi')
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data['swagger'] == '2.0'
    assert data['produces'] == ['application/json']
    assert data['consumes'] == ['application/json']
    assert data['basePath'] == '/api/v1'


def test_api_schema(api_client):
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    assert 'Comment' in data['definitions']
    assert 'Contact' in data['definitions']
    assert '/comment-list/' in data['paths']
    assert '/comment-list/{_uid}/' in data['paths']
    assert '/contact-list/' in data['paths']
    assert '/contact-list/{_uid}/' in data['paths']


def test_api_contact_model_schema(api_client):
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    contact = data['definitions']['Contact']
    assert contact == {
        'type': 'object',
        'required': ['name'],
        'title': 'Contact',
        'properties': {
            '_uid': {'title': ' uid', 'type': 'string', 'format': 'uuid',
                     'readOnly': True},
            '_type': {'title': ' type', 'type': 'string', 'readOnly': True},
            '_version': {
                'title': ' version', 'type': 'integer',
                'readOnly': True},
            'created': {'title': 'Создан', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'updated': {'title': 'Updated', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'name': {
                'title': 'Наименование', 'type': 'string',
                'maxLength': 255, 'minLength': 1},
            'phones': {
                'type': 'array',
                'description': 'Номера телефонов вводятся в произвольном '
                               'формате через запятую',
                'items': {
                    'title': 'Phones', 'type': 'string',
                    'maxLength': 30, 'minLength': 1}},
            'emails': {
                'type': 'array',
                'description': 'E-mail адреса вводятся через запятую',
                'items': {
                    'title': 'Emails', 'type': 'string',
                    'format': 'email', 'maxLength': 254, 'minLength': 1}},
            'order_index': {
                'title': 'Индекс для сортировки', 'type': 'integer',
                'maximum': 2147483647, 'minimum': -2147483648}
        }
    }


def test_api_contact_schema(api_client):
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    comment = data['paths']['/contact-list/']['get']['responses']
    assert comment == {'200': {
        'description': '',
        'schema': {
            'required': ['results', 'count', 'page', 'page_size'],
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'page': {'type': 'integer'},
                'page_size': {'type': 'integer'},
                'pages': {'type': 'integer'},
                'page_next': {'type': 'integer', 'x-nullable': True},
                'page_previous': {'type': 'integer', 'x-nullable': True},
                'results': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/Contact'}}}}}}


def test_api_comment_model_schema(api_client):
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    comment = data['definitions']['Comment']
    assert comment == {
        'type': 'object',
        'required': ['contact', 'message'],
        'properties': {
            '_uid': {'title': ' uid', 'type': 'string', 'format': 'uuid',
                     'readOnly': True},
            '_type': {'title': ' type', 'type': 'string', 'readOnly': True},
            '_version': {
                'title': ' version', 'type': 'integer', 'readOnly': True},
            'created': {'title': 'Создан', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'updated': {'title': 'Updated', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'user': {'title': 'User', 'type': 'integer'},
            'contact': {'$ref': '#/definitions/Contact'},
            'message': {
                'title': 'Сообщение', 'type': 'string', 'minLength': 1}
        }
    }


def test_api_comment_schema(api_client):
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    comment = data['paths']['/comment-list/']['get']['responses']
    assert comment == {'200': {
        'description': '',
        'schema': {
            'required': ['results', 'count', 'page', 'page_size'],
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'page': {'type': 'integer'},
                'page_size': {'type': 'integer'},
                'pages': {'type': 'integer'},
                'page_next': {'type': 'integer', 'x-nullable': True},
                'page_previous': {'type': 'integer', 'x-nullable': True},
                'results': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/Comment'}}}}}}
