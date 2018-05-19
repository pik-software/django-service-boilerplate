import base64
import json
import logging
import os
import sys

import dj_database_url
from google.oauth2 import service_account

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
BASE_DIR_NAME = os.path.basename(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, '__data__')
SERVICE_NAME = os.environ.get('SERVICE_NAME', BASE_DIR_NAME)

SERVICE_TITLE = 'ВСервисус'

REDIS_URL = os.environ.get(
    'REDIS_URL',
    'redis://@127.0.0.1:6379')
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgres://@127.0.0.1:5432/' + SERVICE_NAME)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', '~+%iawwf2@R!@nakwe%jcAWKJF1asdAFw2')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'staging')

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

# ------------------ #
# --- <SERVICES> --- #

# SENTRY
SENTRY_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN', ''),
    'tags': {'environment': ENVIRONMENT},
    'include_versions': False,
    'release': None,
    'CELERY_LOGLEVEL': logging.WARNING,
}

# DATADOG
DD_STATSD_ADDR = os.environ.get('DD_AGENT_PORT_8125_UDP_ADDR', 'localhost')
DD_STATSD_PORT = int(os.environ.get('DD_AGENT_PORT_8125_UDP_PORT', '8125'))
DD_STATSD_NAMESPACE = SERVICE_NAME
DD_TRACE_ADDR = os.environ.get('DD_AGENT_PORT_8126_TCP_ADDR', 'localhost')
DD_TRACE_PORT = int(os.environ.get('DD_AGENT_PORT_8126_TCP_PORT', '8126'))
DATADOG_TRACE = {
    'DEFAULT_SERVICE': SERVICE_NAME + '-django-app',
    'DEFAULT_DATABASE_PREFIX': SERVICE_NAME,
    'AGENT_HOSTNAME': DD_TRACE_ADDR,
    'AGENT_PORT': DD_TRACE_PORT,
    'TAGS': {'env': ENVIRONMENT},
}

# SQL EXPLORER
EXPLORER_CONNECTIONS = {'Default': 'readonly'}
EXPLORER_DEFAULT_CONNECTION = 'readonly'
EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = (
    'auth_', 'contenttypes_',
    'sessions_', 'admin_', 'health_',
    'django_', 'explorer_',
    'authtoken_token',
    'geography_', 'geometry_', 'raster_columns', 'raster_overviews',
    'spatial_ref_sys',
)

# --- </SERVICES> --- #
# ------------------- #

# Application definition

INSTALLED_APPS = [
    'admin_view_permission',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',

    # MAIN APPS
    'contacts',
    'contacts_replica',

    # HISTORY
    'simple_history',
    'eventsourcing',

    # API
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'crispy_forms',  # sexy django_filters forms
    'drf_openapi',

    # CELERY
    'django_celery_results',

    # SENTRY
    'raven.contrib.django.raven_compat',

    # Django health check
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',  # requires celery

    # DATADOG
    'ddtrace.contrib.django',

    'bootstrapform',  # sexy form in _project_/templates

    # DEV
    'debug_toolbar',
    'django_extensions',
    'explorer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # HISTORY
    'simple_history.middleware.HistoryRequestMiddleware',

    # DEV
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

WSGI_APPLICATION = '_project_.wsgi.application'
ROOT_URLCONF = '_project_.urls'

TEMPLATE_ACCESSIBLE_SETTINGS = ['DEBUG', 'MEDIA_URL', 'SERVICE_TITLE']
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.settings',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        engine='django.contrib.gis.db.backends.postgis')
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": SERVICE_NAME
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.'
             'UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.'
             'NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ru-RU'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y',   # '2006-10-25', '10/25/2006',
    '%m/%d/%y',               # '10/25/06'
    '%b %d %Y', '%b %d, %Y',  # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',  # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',  # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',  # '25 October 2006', '25 October, 2006'
    '%d.%m.%Y',               # '25.10.2006'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(DATA_DIR, 'static'))
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(DATA_DIR, 'media'))

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

LOGIN_REDIRECT_URL = '/'
INDEX_STAFF_REDIRECT_URL = '/admin/'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'core.ldap.RemoteUserBackend',
]

# Celery
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_IMPORTS = [
    'core.tasks',
    'eventsourcing.replicator.tasks',
]
CELERYBEAT_SCHEDULE_FILENAME = os.path.join(DATA_DIR, 'celerybeat.db')
CELERYBEAT_SCHEDULE = {}

# DRF
REST_FRAMEWORK_LATEST_API_VERSION = '1'
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS':
        'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_METADATA_CLASS': 'core.api.inspectors.StandardizedMetadata',
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.URLPathVersioning',

    # Generic view behavior
    'DEFAULT_PAGINATION_CLASS': 'core.api.pagination.StandardizedPagination',
    # TODO: use: StandardizedFieldFilters, StandardizedSearchFilter,
    # StandardizedOrderingFilter as default filter backends
    'DEFAULT_FILTER_BACKENDS': (),

    # Schema
    'DEFAULT_SCHEMA_CLASS': 'core.api.inspectors.StandardizedAutoSchema',
    'EXCEPTION_HANDLER': 'core.api.exception_handler.standardized_handler',

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# storage
_STORAGE = os.environ.get('FILE_STORAGE_BACKEND', 'local')
_CREDENTIALS = os.environ.get('FILE_STORAGE_BACKEND_CREDENTIALS', None)
GS_BUCKET_NAME = os.environ.get('FILE_STORAGE_BUCKET_NAME', None)
GS_PROJECT_ID = os.environ.get('FILE_STORAGE_PROJECT_ID', None)
GS_CREDENTIALS = None
if _STORAGE == 'gcloud' and _CREDENTIALS and GS_BUCKET_NAME and GS_PROJECT_ID:
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    # GS_AUTO_CREATE_BUCKET = True
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
        json.loads(base64.b64decode(_CREDENTIALS), strict=False))
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    logging.warning('!! DEFAULT_FILE_STORAGE="FileSystemStorage"')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '[django] %(levelname)s %(asctime)s %(name)s/%(module)s %(process)d/%(thread)d: %(message)s'  # noqa
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  # noqa
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
        'django.template': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'eventsourcing': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    },
}

try:
    from .settings_local import *  # noqa: pylint=unused-wildcard-import, pylint=wildcard-import
except ImportError:
    pass
