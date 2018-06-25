from django.conf.urls import url, include
from django.contrib import admin

from .views import (oidc_admin_login, oidc_admin_logout,
                    oidc_backchannel_logout, complete)


urlpatterns = [  # noqa: invalid-name

    # We need to override default `social_python` `complete` bahavior in order
    # to provide backchannel logout implementation.
    url(r'^openid/complete/(?P<backend>[^/]+)/', complete),
    url(r'^openid/logout/(?P<backend>[^/]+)/$',
        oidc_backchannel_logout, name='oidc_backchannel_logout'),

    url(r'^openid/', include('social_django.urls', namespace='social')),
    url(r'^login/$', admin.site.login, name='login'),
    url(r'^logout/$', admin.site.logout, name='logout'),
    url(r'^admin/login/$', oidc_admin_login),
    url(r'^admin/logout/$', oidc_admin_logout),
]
