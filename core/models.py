from collections import defaultdict
from uuid import uuid4

from django.conf import settings
from django.contrib.admin.utils import NestedObjects
from django.db.models import F, Q, FieldDoesNotExist, signals
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.db import models, router, transaction


class Dated(models.Model):
    created = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name=_('Created')
    )
    updated = models.DateTimeField(
        editable=False, auto_now=True, verbose_name=_('Updated')
    )

    class Meta:
        abstract = True


def _get_field_by_name(model, field):
    """
    Retrieve a field instance from a model by its name.
    """
    field_dict = {x.name: x for x in model._meta.get_fields()}  # noqa
    return field_dict[field]


def _has_field(model, field):
    try:
        model._meta.get_field(field)  # noqa
        return True
    except FieldDoesNotExist:
        return False


def _cascade_soft_delete(inst_or_qs, using, keep_parents=False):
    """
    Return collector instance that has marked ArchiveMixin instances for
    archive (i.e. update) instead of actual delete.
    Arguments:
        inst_or_qs (models.Model or models.QuerySet): the instance(s) that
            are to be deleted.
        using (db connection/router): the db to delete from.
        keep_parents (bool): defaults to False.  Determine if cascade is true.
    Returns:
        models.deletion.Collector: this is a standard Collector instance but
            the ArchiveMixin instances are in the fields for update list.
    """
    if not isinstance(inst_or_qs, models.QuerySet):
        instances = [inst_or_qs]
    else:
        instances = inst_or_qs

    deleted = now()

    # The collector will iteratively crawl the relationships and
    # create a list of models and instances that are connected to
    # this instance.
    collector = NestedObjects(using=using)
    collector.collect(instances, keep_parents=keep_parents)
    collector.sort()
    soft_delete_objs = collector.soft_delete_objs = defaultdict(set)

    for model, instances in list(collector.data.items()):
        # remove archive mixin models from the delete list and put
        # them in the update list.  If we do this, we can just call
        # the collector.delete method.
        inst_list = list(instances)

        if _has_field(model, 'deleted'):
            deleted_on_field = _get_field_by_name(model, 'deleted')
            collector.add_field_update(deleted_on_field, deleted, inst_list)
            soft_delete_objs[model].update(inst_list)
            del collector.data[model]

    # If we use the NestedObjects collector instead models.deletion.Collector,
    # then the `collector.fast_deletes` will always be empty
    for i, q_set in enumerate(collector.fast_deletes):
        # make sure that we do archive on fast deletable models as
        # well.
        model = q_set.model

        if _has_field(model, 'deleted'):
            deleted_on_field = _get_field_by_name(model, 'deleted')
            collector.add_field_update(deleted_on_field, deleted, q_set)
            collector.fast_deletes[i] = q_set.none()

    return collector


def _delete_collected(collector):
    with transaction.atomic(using=collector.using, savepoint=False):
        result = collector.delete()
        for model, instances in collector.soft_delete_objs.items():
            if not model._meta.auto_created:  # noqa: pylint=protected-access
                for obj in instances:
                    signals.post_delete.send(
                        sender=model, instance=obj, using=collector.using
                    )
    return result


class SoftDeletedQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query.add_q(Q(deleted=None))

    def delete(self):
        # doing an update is the most efficient, but does not promise
        # that the cascade will happen. E.g.
        # return self.update(deleted_on=timezone.now())

        # from django source
        # https://github.com/django/django/blob/1.8.6/django/db/models/query.py
        # Line: #L516
        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        # iterating and deleting ensures that the cascade delete will
        # occur for each instance.
        collector = _cascade_soft_delete(self.all(), self.db)
        self._result_cache = None
        return _delete_collected(collector)

    delete.alters_data = True

    def hard_delete(self):
        return models.QuerySet.delete(self)


class SoftDeleted(models.Model):
    """
    Soft deletable model. Inspired by:
    https://lucasroesler.com/2017/04/delete-or-not-to-delete/
    """
    deleted = models.DateTimeField(
        editable=False, null=True, blank=True, verbose_name=_('Deleted')
    )

    objects = SoftDeletedQuerySet.as_manager()
    all_objects = models.QuerySet.as_manager()

    def delete(self, using=None, keep_parents=False):
        using = using or router.db_for_write(self.__class__, instance=self)

        assert self._get_pk_val() is not None, \
            "%s object can't be deleted because its %s attribute " \
            "is set to None." % (self._meta.object_name, self._meta.pk.attname)

        if self.deleted:
            return 0, {}  # short-circuit here to prevent lots of nesting

        if not self._meta.auto_created:
            signals.pre_delete.send(
                sender=self.__class__, instance=self, using=using)

        collector = _cascade_soft_delete(self, using, keep_parents)
        return _delete_collected(collector)

    delete.alters_data = True

    def hard_delete(self, *args, **kwargs):
        return models.Model.delete(self, *args, **kwargs)

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
    autoincrement_version = True

    # Strict increment leads to problems in SimpleHistory (disable by default)
    strict_autoincrement_version = False

    version = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):  # noqa: pylint=arguments-differ
        if not self.version:
            self.version = 1
        else:
            if self.autoincrement_version and self.pk:
                self.version = F('version') + 1 \
                    if self.strict_autoincrement_version \
                    else self.version + 1

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
        # TODO: trigger post_save event
        return updated > 0

    class Meta:
        abstract = True
