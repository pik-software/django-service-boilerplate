from django.db import models


class UpdateStateManager(models.Manager):

    @staticmethod
    def get_last_updated(key):
        state, _ = UpdateState.objects.get_or_create(key=key)
        return state.updated

    @staticmethod
    def set_last_updated(key, datetime):
        UpdateState.objects.update_or_create(
            defaults={'updated': datetime}, key=key)


class UpdateState(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    updated = models.DateTimeField(null=True)

    objects = UpdateStateManager()

    def __str__(self):
        return f'{self.key}: {self.updated.isoformat() if self.updated else 0}'
