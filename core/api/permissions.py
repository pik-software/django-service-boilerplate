from rest_framework import permissions


class DjangoModelViewPermission(permissions.DjangoModelPermissions):

    perms_map = {**permissions.DjangoModelPermissions.perms_map,
                 **{'GET': ['%(app_label)s.view_%(model_name)s']}}
