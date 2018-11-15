from rest_framework import status


def test_smoke_schema(api_client):
    res = api_client.get('/api/v1/schema/')
    assert res.status_code == status.HTTP_200_OK
