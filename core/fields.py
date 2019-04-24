from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.utils.normalization import normalize

MAX_DIGITS = 16
DECIMAL_PLACES = 2


class MoneyField(models.DecimalField):
    def __init__(
            self, *args, max_digits=MAX_DIGITS,
            decimal_places=DECIMAL_PLACES, **kwargs):
        super().__init__(
            *args, max_digits=max_digits,
            decimal_places=decimal_places, **kwargs)


class NormalizedCharField(models.CharField):

    description = _('Normalized by pik.utils.normalization.normalize')

    def pre_save(self, model_instance, add):
        value = normalize(getattr(model_instance, self.attname))
        setattr(model_instance, self.attname, value)
        return value
