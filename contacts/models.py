import reversion
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext as _
from simple_history.models import HistoricalRecords

from core.models import Versioned, Uided, Dated


@reversion.register()
class Contact(Uided, Dated, Versioned):
    UID_PREFIX = 'CON'
    name = models.CharField(_('Наименование'), max_length=255)
    phones = ArrayField(
        models.CharField(max_length=30), blank=True, default=list,
        verbose_name=_('Номера телефонов'),
        help_text=_(
            'Номера телефонов вводятся в произвольном формате через запятую'
        )
    )
    emails = ArrayField(
        models.EmailField(), blank=True, default=list,
        verbose_name=_('E-mail адреса'),
        help_text=_('E-mail адреса вводятся через запятую')
    )

    order_index = models.IntegerField(_('Индекс для сортировки'), default=100)

    history = HistoricalRecords()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('контакт')
        verbose_name_plural = _('контакты')
        ordering = ['-id']
        permissions = (
            ("can_edit_contact", _("Может редактировать контакты")),
            ("can_get_api_contact_history",
             _("Может читать /api/v<X>/contact-list/history/")),

        )
