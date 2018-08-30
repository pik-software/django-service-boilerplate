from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.core.models import BaseHistorical, BasePHistorical, Owned

from eventsourcing.replicator import replicating


@replicating('contact')
class Contact(BaseHistorical):
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
class Comment(BasePHistorical, Owned):
    contact = models.ForeignKey(
        Contact, related_name='comments',
        on_delete=models.CASCADE)
    message = models.TextField(_('Сообщение'))

    def __str__(self):
        return f'{self.user}: {self.message}'

    class Meta:
        verbose_name = _('коментарий')
        verbose_name_plural = _('коментарии')
        ordering = ['-created']
        permissions = (
            ("can_edit_comment", _("Может редактировать коментарий")),
        )
