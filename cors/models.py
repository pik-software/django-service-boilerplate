from django.db import models
from django.utils.translation import ugettext_lazy as _
from pik.core.models import BasePHistorical


class Cors(BasePHistorical):
    permitted_fields = {'{app_label}.change_{model_name}': ['cors']}

    cors = models.CharField(max_length=255, unique=True, help_text=_(
        "Название домена допущенного делать междоменные запросы, например: "
        "staff-front.pik-software.ru или localhost:3000"))

    def __str__(self):
        return self.cors

    class Meta:
        verbose_name = _("Разрешение на кросс-доменные запросы")
        verbose_name_plural = _("Разрешения на кросс-доменные запросы")
