from functools import wraps


def post_process_by(processor):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return processor(func(*args, **kwargs))
        return wrapper
    return decorator
