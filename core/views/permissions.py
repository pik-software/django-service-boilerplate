from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view

from core.utils.permissions import get_permissions_from_allowed_apps


@api_view()
@permission_classes([IsAuthenticated])
def permissions_view(request):
    allowed_apps = getattr(settings, 'ALLOWED_APPS_FOR_PERMISSIONS_VIEW', ())
    if allowed_apps:
        perms = get_permissions_from_allowed_apps(request.user, allowed_apps)
        return JsonResponse({'permissions': perms})
    return JsonResponse({'permissions': []})
