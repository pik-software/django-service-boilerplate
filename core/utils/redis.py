import json
from functools import wraps

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django_redis.serializers.base import BaseSerializer


class JSONSerializer(BaseSerializer):
    """
    The default JSON serializer of django-redis assumes `decode_responses`
    is disabled, and calls `decode()` and `encode()` on the value.
    This serializer does not.
    """

    def dumps(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)

    def loads(self, value):
        return json.loads(value)


def skip_locked(lock_name):
    lock = cache.lock(lock_name)

    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if not lock.acquire(blocking=False):
                return None
            try:
                return method(*args, **kwargs)
            finally:
                lock.release()
        return wrapper
    return decorator
