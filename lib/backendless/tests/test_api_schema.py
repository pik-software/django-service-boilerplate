from rest_framework import status

from .factories import EntityFactory


def test_api_schema_by_anon(anon_api_client):
    res = anon_api_client.get('/api/v1/schema/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_schema_version(api_client):
    res = api_client.get(f'/api/v1/schema/?format=openapi')
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data['swagger'] == '2.0'
    assert data['produces'] == ['application/json']
    assert data['consumes'] == ['application/json']


def test_api_schema_has_entity_type(api_client):
    obj = EntityFactory.create()
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    assert obj.type.slug in data['definitions']
    assert f'/{obj.type.slug}-list/' in data['paths']
    assert f'/{obj.type.slug}-list/{{_uid}}/' in data['paths']


def test_api_object_schema(api_client):
    obj = EntityFactory.create()
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    entity = data['definitions'][obj.type.slug]
    assert entity == {
        'type': 'object',
        'required': ['foo'],
        'properties': {
            '_uid': {
                'title': 'uid', 'type': 'string', 'format': 'uuid',
                'readOnly': True},
            '_type': {
                'title': 'type', 'type': 'string',
                'readOnly': True},
            '_version': {
                'title': 'version', 'type': 'integer',
                'readOnly': True},
            'created': {'title': 'created', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'updated': {'title': 'updated', 'format': 'date-time',
                        'readOnly': True, 'type': 'string'},
            'foo': {'title': 'uid', 'type': 'integer'},
            'bar': {'title': 'uid', 'type': 'integer'},
        }
    }


def test_api_get_schema(api_client):
    obj = EntityFactory.create()
    data = api_client.get(f'/api/v1/schema/?format=openapi').json()
    resp = data['paths'][f'/{obj.type.slug}-list/']['get']['responses']
    assert resp == {'200': {
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
                    'items': {'$ref': f'#/definitions/{obj.type.slug}'}}}}}}
