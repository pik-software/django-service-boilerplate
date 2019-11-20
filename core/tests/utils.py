from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def add_user_permissions(user, model, *actions):
    ctype = ContentType.objects.get_for_model(model)
    user.user_permissions.add(*(
        Permission.objects.get(codename=f'{action}_{model.__name__.lower()}',
                               content_type=ctype)
        for action in actions
    ))


def add_admin_access_permission(user):
    user.is_staff = True
    user.save()


def create_permission(model_name, perm_name, perm_codename):
    content_type = ContentType.objects.get(model=model_name)
    permission = Permission.objects.create(
        name=perm_name, content_type=content_type,
        codename=perm_codename)
    return permission


def get_standardized_api_response(model_obj):
    """Returns standard api response or None for model obj."""

    if model_obj is None:
        return None

    deleted = model_obj.deleted.isoformat() if model_obj.deleted else None

    return {
        '_uid': str(model_obj.uid),
        '_type': model_obj._meta.model_name,  # noqa: pylint=protected-access
        '_version': model_obj.version,
        'created': model_obj.created.isoformat(),
        'updated': model_obj.updated.isoformat(),
        'deleted': deleted,
        'is_deleted': bool(deleted),
    }


def standardized_api_response(get_response_func):
    """Adds standard api response fields to function response."""

    @wraps(get_response_func)
    def wrapped(model_obj):
        if model_obj is None:
            return None

        result = get_response_func(model_obj)
        result.update(get_standardized_api_response(model_obj))

        return result

    return wrapped
