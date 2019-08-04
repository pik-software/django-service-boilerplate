from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


class NotAllowedUserTypeError(Exception):
    pass


def _get_allowed_perms(apps):
    allowed_perms_qs = (
        Permission.objects.filter(content_type__app_label__in=apps)
        .values_list('codename', 'name'))
    allowed_perms = []
    for code_name, verbose_name in allowed_perms_qs:
        allowed_perms.append({
            'code_name': code_name,
            'verbose_name': verbose_name, 'granted': False})
    return allowed_perms


def _get_granted_perms(user, apps):
    granted_perms = []
    user_perms_qs = user.user_permissions
    user_groups_field = get_user_model()._meta.get_field('groups') # noqa: protected-access
    user_groups_q = f'group__{user_groups_field.related_query_name()}'
    group_perms_qs = Permission.objects.filter(**{user_groups_q: user})
    for perms_qs in (user_perms_qs, group_perms_qs):
        granted_perms.extend(
            perms_qs.filter(content_type__app_label__in=apps)
            .values_list('codename', flat=True))
    return granted_perms


def get_permissions_from_allowed_apps(user, apps):
    if not user.is_active or user.is_anonymous:
        raise NotAllowedUserTypeError(
            "You can't use this function for not active or anonymous user")

    allowed_perms = _get_allowed_perms(apps)
    if user.is_superuser:
        for perm in allowed_perms:
            perm['granted'] = True
    else:
        granted_perms = _get_granted_perms(user, apps)
        for perm in allowed_perms:
            if user.is_active and perm['code_name'] in granted_perms:
                perm['granted'] = True

    return allowed_perms
