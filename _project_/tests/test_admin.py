def test_admin_index_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200
