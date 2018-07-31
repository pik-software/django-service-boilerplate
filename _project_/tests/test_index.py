import pytest


@pytest.mark.selenium
def test_login(base_url, selenium):
    selenium.get(f'{base_url}/login')
    assert selenium.title == 'Войти | Сервис'
