from rest_framework import status

from .factories import EntityTypeFactory


def test_api_root_by_anon(anon_api_client):
    res = anon_api_client.get('/api/v1/')
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED,
                               status.HTTP_403_FORBIDDEN)


def test_api_root_has_entity_url(api_client):
    EntityTypeFactory.create(slug='entity')
    res = api_client.get('/api/v1/')
    assert 'entity-list' in res.data
    assert res.data['entity-list'] == 'http://testserver/api/v1/entity-list/'
