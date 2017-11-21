from django.db import models

MAX_DIGITS = 16
DECIMAL_PLACES = 2


class MoneyField(models.DecimalField):
    def __init__(
            self, *args, max_digits=MAX_DIGITS,
            decimal_places=DECIMAL_PLACES, **kwargs):
        super().__init__(
            *args, max_digits=max_digits,
            decimal_places=decimal_places, **kwargs)
