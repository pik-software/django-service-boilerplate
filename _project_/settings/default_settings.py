# coding=utf-8
# Build paths inside the project like this: join(BASE_DIR, ...)
import os
from os.path import join

from ..stub_settings import ROOT_DIR, PATH_TO_PROJECT_VENV_DIR, \
    PATH_TO_PROJECT_COLLECT_STATIC_DIR, PATH_TO_PROJECT_MEDIA_DIR, \
    PATH_TO_PROJECT_SQLITE_FILE, ROOT_DIR_NAME

DEBUG = TEMPLATE_DEBUG = False if os.environ.get('PRODUCTION') else True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

CACHE_MIDDLEWARE_KEY_PREFIX = ROOT_DIR_NAME
SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p+a4h0a7z-q0@wq#pw#n6+^a#j70kjgibj7h_33e^2@z4ve@%&'

TEMPLATE_DIRS = (
    join(ROOT_DIR, "_project_", "templates"),
)

STATICFILES_DIRS = (
    join(ROOT_DIR, "_project_", u'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

FIXTURE_DIRS = (
    join(ROOT_DIR, "_project_", u'fixtures'),
)

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.webdesign',

    # 'debug_toolbar',
    # 'south',
    '_project_',
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

ROOT_URLCONF = '_project_.urls'
WSGI_APPLICATION = '_project_.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PATH_TO_PROJECT_SQLITE_FILE,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = PATH_TO_PROJECT_COLLECT_STATIC_DIR

MEDIA_URL = '/media/'
MEDIA_ROOT = PATH_TO_PROJECT_MEDIA_DIR

# CACHES = {
#     # Long cache timeout for staticfiles, since this is used heavily by the optimizing storage.
#     "staticfiles": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         "TIMEOUT": 60 * 60 * 24 * 365,
#         "LOCATION": "staticfiles",
#     },
# }

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        }
    }
}
