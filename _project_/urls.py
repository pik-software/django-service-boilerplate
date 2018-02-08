from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from core.api.auth import OBTAIN_AUTH_TOKEN
from core.api.router import StandardizedRouter
from core.api.schema import SchemaView
from core.views import task_result_api_view
from contacts.api import ContactViewSet

router = StandardizedRouter()  # noqa: pylint=invalid-name
router.register(
    'contact-list', ContactViewSet, base_name='contact')


@login_required
def index(request):
    from django.shortcuts import render, redirect
    if request.user.is_staff:
        return redirect(settings.INDEX_STAFF_REDIRECT_URL)
    return render(request, 'access_denied.html', {})


urlpatterns = [  # noqa: pylint=invalid-name
    url(r'^$', index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.auth_urls')),
    url(r'^api/task/result/(.+)/', task_result_api_view),
    url(r'^api/v(?P<version>[1-9])/schema/',
        SchemaView.as_view(), name='api_schema'),
    url(r'^api/v(?P<version>[1-9])/', include(router.urls, namespace='api')),
    url(r'^api-token-auth/', OBTAIN_AUTH_TOKEN),
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
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^explorer/', include('explorer.urls')),
    ]
