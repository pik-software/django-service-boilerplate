import pytest
from django.core.exceptions import ValidationError

from core.validators import snils_validator, inn_validator, kpp_validator


def test_valid_snils():
    assert snils_validator('11223344595') is None
    assert snils_validator('08765430300') is None
    assert snils_validator('08675430300') is None


def test_valid_inn():
    assert inn_validator('3257051274') is None
    assert inn_validator('7710492102') is None
    assert inn_validator('5047166441') is None


def test_valid_len_snils():
    with pytest.raises(ValidationError) as excinfo:
        snils_validator('1122334459')
    assert 'не равна' in str(excinfo.value)


def test_valid_len_inn():
    with pytest.raises(ValidationError) as excinfo:
        inn_validator('771042102')
    assert 'не равна' in str(excinfo.value)


def test_valid_len_kpp():
    with pytest.raises(ValidationError) as excinfo:
        kpp_validator('50440101')
    assert 'не равна' in str(excinfo.value)


def test_invalid_snils_with_space():
    with pytest.raises(ValidationError) as excinfo:
        snils_validator('112233445 95')
    assert 'Лишние символы' in str(excinfo.value)


def test_invalid_inn_with_space():
    with pytest.raises(ValidationError) as excinfo:
        inn_validator('370263595 2')
    assert 'Лишние символы' in str(excinfo.value)


def test_invalid_kpp_with_space():
    with pytest.raises(ValidationError) as excinfo:
        kpp_validator('77 1001 001')
    assert 'Лишние символы' in str(excinfo.value)