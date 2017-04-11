def test_admin_index(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200
