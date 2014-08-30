__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):
        def append_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d += (value, )
            g[name] = d

        g['DEBUG_TOOLBAR_PATCH_SETTINGS'] = False
        g['INTERNAL_IPS'] = ['127.0.0.1']

        INSTALLED_APPS = (
            # ...
            'django.contrib.staticfiles',
            # ...
            # If you're using Django 1.7.x or later
            # 'debug_toolbar.apps.DebugToolbarConfig',
            # If you're using Django 1.6.x or earlier
            'debug_toolbar',
        )

        for x in INSTALLED_APPS:
            append_if_not_exist("INSTALLED_APPS", x)

        MIDDLEWARE_CLASSES = (
            # ...
            'debug_toolbar.middleware.DebugToolbarMiddleware',
            # ...
        )

        for x in MIDDLEWARE_CLASSES:
            append_if_not_exist("MIDDLEWARE_CLASSES", x)

    @staticmethod
    def update_urls(urlpatterns):
        from django.conf.urls import patterns, include, url
        from django.conf import settings

        if settings.DEBUG:
            import debug_toolbar
            urlpatterns += patterns('',
                url(r'^__debug__/', include(debug_toolbar.urls)),
            )
        return urlpatterns