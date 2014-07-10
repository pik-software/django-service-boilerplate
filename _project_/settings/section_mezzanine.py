__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):

        # The numeric mode to set newly-uploaded files to. The value should be
        # a mode you'd pass directly to os.chmod.
        g['FILE_UPLOAD_PERMISSIONS'] = 0o644

        g['INSTALLED_APPS'] += (
            "mezzanine.boot",
            "mezzanine.conf",
            "mezzanine.core",
            "mezzanine.generic",
            "mezzanine.blog",
            "mezzanine.forms",
            "mezzanine.pages",
            "mezzanine.galleries",
            "mezzanine.twitter",
            # "mezzanine.accounts",
            # "mezzanine.mobile",
        )

        print(g['INSTALLED_APPS'])

        def append_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d += (value, )
            g[name] = d

        def prepend_if_not_exist(name, value):
            d = tuple(g[name])
            if value not in d:
                d = (value, ) + d
            g[name] = d

        def insert_after_if_not_exist(name, value, insert_after):
            d = tuple(g[name])
            if value not in d:
                if insert_after not in d:
                    raise Exception(
                        "Can`t insert settings {0} value {1} "
                        "because {2} not in {0}".format(
                            name, value, insert_after))
                i = d.index(insert_after)
                d = d[:i] + (d[i], value) + d[i + 1:]
            g[name] = d

        g['AUTHENTICATION_BACKENDS'] = (
            "mezzanine.core.auth_backends.MezzanineBackend",)

        # --------------------------------------------
        # TEMPLATE_CONTEXT_PROCESSORS
        # --------------------------------------------

        TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.static",
            "django.core.context_processors.media",
            "django.core.context_processors.request",
            "django.core.context_processors.tz",
            "mezzanine.conf.context_processors.settings",
            "mezzanine.pages.context_processors.page",
        )

        for x in TEMPLATE_CONTEXT_PROCESSORS:
            append_if_not_exist("TEMPLATE_CONTEXT_PROCESSORS", x)

        # --------------------------------------------
        # MIDDLEWARE_CLASSES
        # --------------------------------------------

        prepend_if_not_exist(
            "MIDDLEWARE_CLASSES",
            "mezzanine.core.middleware.UpdateCacheMiddleware"
        )
        insert_after_if_not_exist(
            "MIDDLEWARE_CLASSES",
            "django.middleware.locale.LocaleMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware"
        )

        MIDDLEWARE_CLASSES = (
            "mezzanine.core.request.CurrentRequestMiddleware",
            "mezzanine.core.middleware.RedirectFallbackMiddleware",
            "mezzanine.core.middleware.TemplateForDeviceMiddleware",
            "mezzanine.core.middleware.TemplateForHostMiddleware",
            "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
            "mezzanine.core.middleware.SitePermissionMiddleware",
            # Uncomment the following if using any of the SSL settings:
            # "mezzanine.core.middleware.SSLRedirectMiddleware",
            "mezzanine.pages.middleware.PageMiddleware",
            "mezzanine.core.middleware.FetchFromCacheMiddleware",
        )

        for x in MIDDLEWARE_CLASSES:
            append_if_not_exist('MIDDLEWARE_CLASSES', x)


        #########################
        # OPTIONAL APPLICATIONS #
        #########################

        # Store these package names here as they may change in the future since
        # at the moment we are using custom forks of them.
        g['PACKAGE_NAME_FILEBROWSER'] = "filebrowser_safe"
        g['PACKAGE_NAME_GRAPPELLI'] = "grappelli_safe"

        # These will be added to ``INSTALLED_APPS``, only if available.
        g['OPTIONAL_APPS'] = (
            "debug_toolbar",
            "django_extensions",
            "compressor",
            g['PACKAGE_NAME_FILEBROWSER'],
            g['PACKAGE_NAME_GRAPPELLI'],
        )

        ####################
        # DYNAMIC SETTINGS #
        ####################

        # set_dynamic_settings() will rewrite globals based on what has been
        # defined so far, in order to provide some better defaults where
        # applicable. We also allow this settings module to be imported
        # without Mezzanine installed, as the case may be when using the
        # fabfile, where setting the dynamic settings below isn't strictly
        # required.
        try:
            from mezzanine.utils.conf import set_dynamic_settings
        except ImportError:
            pass
        else:
            set_dynamic_settings(globals())
