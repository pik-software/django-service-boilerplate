from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.core.models import BasePHistorical

from core.fields import NormalizedCharField
from .utils.swagger import validate_and_merge_schemas

DEFAULT_SCHEMA = {
    'type': 'object',
    'properties': {
        '_uid': {
            'title': 'uid', 'type': 'string', 'format': 'uuid',
            'readOnly': True},
        '_type': {
            'title': 'type', 'type': 'string',
            'readOnly': True},
        '_version': {
            'title': 'version', 'type': 'integer',
            'readOnly': True},
        'created': {'title': 'created', 'format': 'date-time',
                    'readOnly': True, 'type': 'string'},
        'updated': {'title': 'updated', 'format': 'date-time',
                    'readOnly': True, 'type': 'string'},
    }
}


class EntityType(BasePHistorical):
    slug = models.SlugField(_('_type'), unique=True)
    name = NormalizedCharField(_('Название'), max_length=255)
    schema = JSONField(_('OpenAPI Schema'), default=dict)

    def __str__(self):
        return f'{self.name} ({self.slug})'

    def save(self, *args, **kwargs):
        self.schema = validate_and_merge_schemas(self.schema, DEFAULT_SCHEMA)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('тип')
        verbose_name_plural = _('типы')
        ordering = ['-created']


class Entity(BasePHistorical):
    type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    value = JSONField(default=dict)

    class Meta:
        verbose_name = _('значение')
        verbose_name_plural = _('значения')
        ordering = ['-created']
