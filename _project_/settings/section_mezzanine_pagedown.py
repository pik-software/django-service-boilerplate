__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):
        def append_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d += (value, )
            g[name] = d

        INSTALLED_APPS = (
            'mezzanine_pagedown',
        )

        for x in INSTALLED_APPS:
            append_if_not_exist("INSTALLED_APPS", x)

        g['RICHTEXT_WIDGET_CLASS'] = 'mezzanine_pagedown.widgets.PageDownWidget'

        # mezzanine_pagedown.filters.custom to enable an explicit list of
        # extensions through the PAGEDOWN_MARKDOWN_EXTENSIONS setting
        g['RICHTEXT_FILTER'] = 'mezzanine_pagedown.filters.custom'
        g['RICHTEXT_FILTERS'] = ('mezzanine_pagedown.filters.custom', )
        g['RICHTEXT_FILTER_LEVEL'] = 3

        g['PAGEDOWN_MARKDOWN_EXTENSIONS'] = (
            'extra',
            'codehilite',
            'toc'
        )

        g['PAGEDOWN_SERVER_SIDE_PREVIEW'] = False


    @staticmethod
    def update_urls(urlpatterns):
        from django.conf.urls import patterns, include, url
        from django.conf import settings

        if settings.PAGEDOWN_SERVER_SIDE_PREVIEW:
            import mezzanine_pagedown
            urlpatterns += patterns('',
                ("^pagedown/", include(mezzanine_pagedown.urls)),
            )
        return urlpatterns