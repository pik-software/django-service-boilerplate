from django.db import models
from pik.core.models import BasePHistorical


class Cors(BasePHistorical):
    cors = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.cors

    class Meta:
        verbose_name = "Разрешение на кросс-доменные запросы"
        verbose_name_plural = "Разрешения на кросс-доменные запросы"
