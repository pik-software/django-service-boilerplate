from django.utils.translation import ugettext_lazy as _

CONTACT_TYPE_UNKNOWN = 0
CONTACT_TYPE_EMPLOYEE = 1
CONTACT_TYPE_CONTRACTOR = 2
CONTACT_TYPE_CLIENT = 3

CONTACT_TYPE_CHOICES = (
    (0, _('Неизвестный')),
    (1, _('Сотрудник')),
    (2, _('Подрядчик')),
    (3, _('Клиент')),
)
