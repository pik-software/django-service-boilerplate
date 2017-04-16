def test_index(base_url, selenium):
    selenium.get(base_url)
    assert selenium.title == 'Home'
