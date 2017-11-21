"""_project_ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter

from core.views import task_result_api_view

router = DefaultRouter()  # noqa: pylint: invalid-name
# router.register('buildings', BuildingViewSet)


@login_required
def index(request):
    from django.shortcuts import render, redirect
    if request.user.is_staff:
        return redirect(settings.INDEX_STAFF_REDIRECT_URL)
    return render(request, 'access_denied.html', {})


urlpatterns = [  # noqa: pylint: invalid-name
    url(r'^$', index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.auth_urls')),
    url(r'^api/task/result/(.+)/', task_result_api_view),
    url(r'^api/v1/', include(router.urls)),
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
