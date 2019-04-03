from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def add_permissions(user, model, *actions):
    ctype = ContentType.objects.get_for_model(model)
    user.user_permissions.add(*(
        Permission.objects.get(codename=f'{action}_{model.__name__.lower()}',
                               content_type=ctype)
        for action in actions
    ))


def add_admin_access_permission(user):
    user.is_staff = True
    user.save()
