from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from core.api.auth import OBTAIN_AUTH_TOKEN
from core.api.router import StandardizedRouter
from core.api.schema import SchemaView
from core.views import task_result_api_view
from contacts.api import ContactViewSet, CommentViewSet
from eventsourcing.replicated import WebhookCallbackViewSet
from eventsourcing.replicator import SubscriptionViewSet

router = StandardizedRouter()  # noqa: pylint=invalid-name
router.register(
    'contact-list', ContactViewSet, base_name='contact')
router.register(
    'comment-list', CommentViewSet, base_name='comment')

webhook = DefaultRouter()  # noqa: pylint=invalid-name
webhook.register(
    'callback', WebhookCallbackViewSet, base_name='callback')
webhook.register(
    'subscriptions', SubscriptionViewSet, base_name='subscription')


@login_required
def index(request):
    from django.shortcuts import render, redirect
    if request.user.is_staff:
        return redirect(settings.INDEX_STAFF_REDIRECT_URL)
    return render(request, 'access_denied.html', {})


urlpatterns = [  # noqa: pylint=invalid-name
    path('', index, name='index'),
    path('', include('lib.oidc_relied.urls')),
    path('admin/', admin.site.urls),
    path('status/', include('health_check.urls')),
    path('accounts/', include('registration.auth_urls')),
    path('api/task/result/<str:taskid>/', task_result_api_view),
    path('api/v<version>/schema/', SchemaView.as_view(), name='api_schema'),
    path('api/v<int:version>/', include((router.urls, 'api'))),
    path('api/v<int:version>/', include(webhook.urls)),
    path('api-token-auth/', OBTAIN_AUTH_TOKEN),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

if settings.DEBUG:
    import debug_toolbar  # noqa

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('explorer/', include('explorer.urls')),
    ]
