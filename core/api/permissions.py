from rest_framework import permissions


class APIImport(permissions.BasePermission):
    message = "Access denied! You need permission for import."

    def has_permission(self, request, view):
        if request.user.has_perm('auth.can_post_api_import'):
            return True
        return False
