from functools import wraps

from django.core.cache import cache


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
