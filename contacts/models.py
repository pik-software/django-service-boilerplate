from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.core.models import BaseHistorical, BasePHistorical, Owned

from core.fields import NormalizedCharField


class Category(BasePHistorical):
    name = NormalizedCharField(_('Название'), max_length=255)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')
        ordering = ['-created']


class Contact(BaseHistorical):
    permitted_fields = {
        '{app_label}.change_{model_name}': [
            'name', 'phones', 'emails', 'order_index']
    }

    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    name = NormalizedCharField(_('Наименование'), max_length=255)
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


class Comment(BasePHistorical, Owned):
    permitted_fields = {
        '{app_label}.change_{model_name}': ['message', 'contact'],
        '{app_label}.change_user_{model_name}': ['user_id']
    }

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
            ("change_user_comment",
             _("Может менять автора коментария")),
        )
