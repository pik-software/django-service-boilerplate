from uuid import uuid4

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("User"),
        related_name="%(class)ss", db_index=True,
        on_delete=models.CASCADE, editable=False)

    class Meta:
        abstract = True


class NullOwned(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("User"),
        related_name="%(class)ss", db_index=True,
        on_delete=models.CASCADE, editable=False,
        null=True)

    class Meta:
        abstract = True


class Uided(models.Model):
    UID_PREFIX = 'OBJ'
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)

    @cached_property
    def suid(self) -> str:
        """
        String representation of UID
        """
        return "{{{0}-{1}}}".format(self.UID_PREFIX, self.uid).lower()

    def __str__(self):
        return self.suid

    class Meta:
        abstract = True


class PUided(models.Model):
    """
    Primary Uided
    """
    UID_PREFIX = 'OBJ'
    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    @cached_property
    def suid(self) -> str:
        """
        String representation of UID
        """
        return "{{{0}-{1}}}".format(self.UID_PREFIX, self.uid).lower()

    def __str__(self):
        return self.suid

    class Meta:
        abstract = True


class Versioned(models.Model):
    version = models.IntegerField(default=1, editable=False)

    def save(self, *args, **kwargs):  # noqa: pylint=arguments-differ
        if not self.version:
            self.version = 1
        else:
            self.version += 1
        super().save(*args, **kwargs)

    def optimistic_concurrency_update(self, **kwargs):
        """
        Safe optimistic concurrent update. If the object was not modified
        since we fetched it than the object is updated and function will
        return `True`. If it was modified than the function will
        return `False` and the object will not be updated.

        NOTE 1: In an environment with a lot of concurrent updates
        this approach might be wasteful.

        NOTE 2: This approach does not protect from modifications made
        to the object outside this function. If you have other tasks
        that modify the data directly (e.g use `save()` directly)
        you need to make sure they use the version as well.

        Example:

            class Account(Versioned):
                balance = models.IntegerField(default=100)

                def withdraw(self, amount):
                    if self.balance < amount:
                        raise errors.RuntimeError()

                    result = self.balance - amount
                    return self.optimistic_concurrency_update(balance=balance)

            x = Account()
            x.withdraw(100)
            x.withdraw(100)

        :return: is the object updated
        :rtype: bool
        """
        # more detail here: https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2  # noqa
        kwargs['version'] = self.version + 1
        model = type(self)
        updated = model.objects.filter(id=self.id, version=self.version) \
            .update(**kwargs)
        return updated > 0

    class Meta:
        abstract = True
