from django.contrib.auth.models import Group

from pik.core.cache import cachedmethod


SYSTEM_GROUP_PREFIX = "sys-"


def associate_by_username(backend, response, *args, **kwargs):
    if not hasattr(backend, 'get_user_by_username'):
        return None
    username = response.get('preferred_username', None)
    user = backend.get_user_by_username(username)
    return {'user': user, 'is_new': user is None, 'username': username}


@cachedmethod('user_details_{response[access_token]}')
def actualize_roles(user, response, *args, **kwargs):
    local = user.groups.exclude(name__startswith=SYSTEM_GROUP_PREFIX)
    local = set(local.values_list('name', flat=True))
    remote = set(role['name'] for role in response.get('roles', [])
                 + [{'name': 'default'}])

    for role in remote - local:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

    for role in local - remote:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.remove(group)


def actualize_staff_status(user, *args, **kwargs):
    if not user.is_staff:
        user.is_staff = True
        user.save()
