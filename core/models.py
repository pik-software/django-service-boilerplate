from uuid import uuid4

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.db import models


class Dated(models.Model):
    created = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name=_('Created')
    )
    updated = models.DateTimeField(
        editable=False, auto_now=True, verbose_name=_('Updated')
    )

    class Meta:
        abstract = True


class Owned(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name=_("User"),
                             related_name="%(class)ss", db_index=True)

    class Meta:
        abstract = True


class NullOwned(models.Model):
    user = models.ForeignKey(get_user_model(), verbose_name=_("User"),
                             related_name="%(class)ss", null=True,
                             db_index=True)

    class Meta:
        abstract = True


class Uided(models.Model):
    UID_PREFIX = 'Obj'
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)

    def __str__(self):
        return "{{{0}-{1}}}".format(self.UID_PREFIX, self.uid)

    class Meta:
        abstract = True
