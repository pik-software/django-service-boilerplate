from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _

internal_phones_validator = RegexValidator(  # noqa: pylint=invalid-name
    regex=r'^(\d{4}|\d{6}|\d{7})$',  # noqa
    message=_('Неверный формат номера внутреннего телефона. '
              'Используйте XXXX, XXXXXX или XXXXXXX.')
)

external_phones_validator = RegexValidator(  # noqa: pylint=invalid-name
    regex=r'^\+7\d{10}$',  # noqa
    message=_('Неверный формат номера внешнего телефона. '
              'Используйте +7XXXXXXXXXX')
)


def snils_validator(value):
    if not value.isdigit():
        raise ValidationError(
            _('Лишние символы в СНИЛС: %(value)s'), params={'value': value}
        )
    if len(value) != 11:
        raise ValidationError(_('Длина СНИЛС не равна 11 символам'))

    numbers = list(map(int, list(value[:-2])))
    check_sum = int(value[-2:])

    a_sum = 0
    for i, digit in enumerate(numbers):
        a_sum += digit * (9 - i)
    if 100 <= a_sum <= 101:
        a_sum = 0
    elif a_sum > 101:
        a_sum = (a_sum % 101) % 100

    if a_sum != check_sum:
        raise ValidationError(_('Неверная контрольная сумма СНИЛС'))


def inn_validator(value):
    if not value.isdigit():
        raise ValidationError(
            _('Лишние символы в ИНН: %(value)s'), params={'value': value}
        )
    if len(value) != 10:
        raise ValidationError(_('Длина ИНН не равна 10 символам'))

    numbers = list(map(int, list(value[:-1])))
    check_sum = int(value[-1:])

    factors = 2, 4, 10, 3, 5, 9, 4, 6, 8
    a_sum = sum([factors[i] * numbers[i] for i in range(9)]) % 11 % 10

    if a_sum != check_sum:
        raise ValidationError(_('Неверная контрольная сумма ИНН'))


def kpp_validator(value):
    if not value.isdigit():
        raise ValidationError(
            _('Лишние символы в КПП: %(value)s'), params={'value': value}
        )
    if len(value) != 9:
        raise ValidationError(_('Длина КПП не равна 9 символам'))


def ogrn_validator(value):
    if not value.isdigit():
        raise ValidationError(
            _('Лишние символы в ОГРН: %(value)s'), params={'value': value}
        )
    if len(value) != 13:
        raise ValidationError(_('Длина ОГРН не равна 13 символам'))

    a_digit = str(int(value[:-1]) % 11 % 10)

    if a_digit != value[-1]:
        raise ValidationError(_('Неверное контрольное число ОГРН'))


def non_negative(value):
    if value < 0:
        raise ValidationError(_('Ошибка ввода: число < 0'))
