from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from core.models import Versioned, Uided, Dated, PUided, Owned
from eventsourcing.replicator import replicating


@replicating('contact')
class Contact(Uided, Dated, Versioned):
    UID_PREFIX = 'CON'
    name = models.CharField(_('Наименование'), max_length=255)
    phones = ArrayField(
        models.CharField(max_length=30), blank=True, default=list,
        verbose_name=_('Номера телефонов'),
        help_text=_(
            'Номера телефонов вводятся в произвольном формате через запятую'
        ))
    emails = ArrayField(
        models.EmailField(), blank=True, default=list,
        verbose_name=_('E-mail адреса'),
        help_text=_('E-mail адреса вводятся через запятую'))

    order_index = models.IntegerField(_('Индекс для сортировки'), default=100)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('контакт')
        verbose_name_plural = _('контакты')
        ordering = ['-id']
        permissions = (
            ("can_edit_contact", _("Может редактировать контакты")),
        )


@replicating('comment')
class Comment(PUided, Dated, Versioned, Owned):
    UID_PREFIX = 'COM'
    contact = models.ForeignKey(
        Contact, related_name='comments',
        on_delete=models.CASCADE)
    message = models.TextField(_('Сообщение'))

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.user}: {self.message}'

    class Meta:
        verbose_name = _('коментарий')
        verbose_name_plural = _('коментарии')
        ordering = ['-created']
        permissions = (
            ("can_edit_comment", _("Может редактировать коментарий")),
        )
