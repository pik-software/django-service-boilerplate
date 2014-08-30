__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):
        def append_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d += (value, )
            g[name] = d

        append_if_not_exist('INSTALLED_APPS', 'smuggler')


    @staticmethod
    def update_urls(urlpatterns):
        from django.conf.urls import patterns, include, url
        from django.conf.urls.i18n import i18n_patterns
        from django.conf import settings
        urlpatterns = patterns('', (r'^admin/', include('smuggler.urls'))) + urlpatterns
        return urlpatterns