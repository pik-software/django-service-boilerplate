__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):
        def prepend_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d = (value, ) + d
            g[name] = d

        def append_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d += (value, )
            g[name] = d

        prepend_if_not_exist('INSTALLED_APPS', 'modeltranslation')
        g['MODELTRANSLATION_DEFAULT_LANGUAGE'] = 'ru'
        g['MODELTRANSLATION_TRANSLATION_FILES'] = (
            '_project_.fix_mezzanine_translation.translation',
        )

        append_if_not_exist('INSTALLED_APPS', '_project_.fix_mezzanine_translation')

    @staticmethod
    def update_urls(urlpatterns):
        return urlpatterns