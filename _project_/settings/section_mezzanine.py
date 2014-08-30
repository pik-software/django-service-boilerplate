__author__ = 'pahaz'


class Installer(object):
    @staticmethod
    def update_settings(g):
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

        # The numeric mode to set newly-uploaded files to. The value should be
        # a mode you'd pass directly to os.chmod.
        g['FILE_UPLOAD_PERMISSIONS'] = 0o644

        g['AUTHENTICATION_BACKENDS'] = (
            "mezzanine.core.auth_backends.MezzanineBackend",)

        # --------------------------------------------
        # INSTALLED_APPS
        # --------------------------------------------

        INSTALLED_APPS = (
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.redirects",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.sitemaps",
            "django.contrib.staticfiles",
            "mezzanine.boot",
            "mezzanine.conf",
            "mezzanine.core",
            "mezzanine.generic",
            "mezzanine.blog",
            "mezzanine.forms",
            "mezzanine.pages",
            "mezzanine.galleries",
            "mezzanine.twitter",
            #"mezzanine.accounts",
            #"mezzanine.mobile",
        )

        for x in INSTALLED_APPS:
            append_if_not_exist("INSTALLED_APPS", x)

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
            set_dynamic_settings(g)

    @staticmethod
    def update_urls(urlpatterns):
        from django.conf.urls import patterns, include, url
        from django.conf import settings
        urlpatterns += patterns('',

            # We don't want to presume how your homepage works, so here are a
            # few patterns you can use to set it up.

            # HOMEPAGE AS STATIC TEMPLATE
            # ---------------------------
            # This pattern simply loads the index.html template. It isn't
            # commented out like the others, so it's the default. You only need
            # one homepage pattern, so if you use a different one, comment this
            # one out.

            #url("^$", direct_to_template, {"template": "index.html"},
            # name="home"),

            # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
            # ---------------------------------------------
            # This pattern gives us a normal ``Page`` object, so that your
            # homepage can be managed via the page tree in the admin. If you
            # use this pattern, you'll need to create a page in the page tree,
            # and specify its URL (in the Meta Data section) as "/", which
            # is the value used below in the ``{"slug": "/"}`` part.
            # Also note that the normal rule of adding a custom
            # template per page with the template name using the page's slug
            # doesn't apply here, since we can't have a template called
            # "/.html" - so for this case, the template "pages/index.html"
            # should be used if you want to customize the homepage's template.

            url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),

            # HOMEPAGE FOR A BLOG-ONLY SITE
            # -----------------------------
            # This pattern points the homepage to the blog post listing page,
            # and is useful for sites that are primarily blogs. If you use this
            # pattern, you'll also need to set BLOG_SLUG = "" in your
            # ``settings.py`` module, and delete the blog page object from the
            # page tree in the admin if it was installed.

            # url("^$", "mezzanine.blog.views.blog_post_list", name="home"),

            # MEZZANINE'S URLS
            # ----------------
            # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
            # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
            # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
            # WILL NEVER BE MATCHED!

            # If you'd like more granular control over the patterns in
            # ``mezzanine.urls``, go right ahead and take the parts you want
            # from it, and use them directly below instead of using
            # ``mezzanine.urls``.
            # ("^", include("mezzanine.urls")),

            # MOUNTING MEZZANINE UNDER A PREFIX
            # ---------------------------------
            # You can also mount all of Mezzanine's urlpatterns under a
            # URL prefix if desired. When doing this, you need to define the
            # ``SITE_PREFIX`` setting, which will contain the prefix. Eg:
            # SITE_PREFIX = "my/site/prefix"
            # For convenience, and to avoid repeating the prefix, use the
            # commented out pattern below (commenting out the one above of
            # course)
            # which will make use of the ``SITE_PREFIX`` setting. Make sure to
            # add the import ``from django.conf import settings`` to the top
            # of this file as well.
            # Note that for any of the various homepage patterns above, you'll
            # need to use the ``SITE_PREFIX`` setting as well.
            # MEZZANINE_PAGE_PREFIX = "pages/"

            ("^", include("mezzanine.urls")),
        )
