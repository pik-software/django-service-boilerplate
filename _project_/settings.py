import base64
import json
import logging
import os
import sys
from datetime import timedelta

import dj_database_url
from django.core.files.storage import FileSystemStorage

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
BASE_DIR_NAME = os.path.basename(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, '__data__')
SERVICE_NAME = os.environ.get('SERVICE_NAME', BASE_DIR_NAME)

SERVICE_TITLE = 'Сервис'

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
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN', ''),
    'CELERY_LOGLEVEL': logging.WARNING,
}

# APM
DD_STATSD_ADDR = os.environ.get('DD_AGENT_PORT_8125_UDP_ADDR', 'dd-agent')
DD_STATSD_PORT = int(os.environ.get('DD_AGENT_PORT_8125_UDP_PORT', '8125'))
DD_STATSD_NAMESPACE = SERVICE_NAME
DD_TRACE_ADDR = os.environ.get('DD_AGENT_PORT_8126_TCP_ADDR', 'dd-agent')
DD_TRACE_PORT = int(os.environ.get('DD_AGENT_PORT_8126_TCP_PORT', '8126'))
DATADOG_TRACE = {
    'DEFAULT_SERVICE': SERVICE_NAME + '-django-app',
    'DEFAULT_DATABASE_PREFIX': SERVICE_NAME,
    'AGENT_HOSTNAME': DD_TRACE_ADDR,
    'AGENT_PORT': DD_TRACE_PORT,
    'TAGS': {'env': ENVIRONMENT},
}
ELASTIC_APM_SERVER_ADDR = os.environ.get(
    'ELASTIC_APM_SERVER_ADDR', '172.17.0.1')
ELASTIC_APM_SERVER_PORT = int(os.environ.get(
    'ELASTIC_APM_SERVER_PORT', '8200'))
ELASTIC_APM = {
    'SERVICE_NAME': SERVICE_NAME + '-django-app',
    'SECRET_TOKEN': '',
    'SERVER_URL': 'http://{0}:{1}'.format(
        ELASTIC_APM_SERVER_ADDR, ELASTIC_APM_SERVER_PORT),
}

# INTEGRA (lib.integra)
INTEGRA_CONFIGS = json.loads(os.environ.get('INTEGRA_CONFIGS', '[]'))
# INTEGRA_CONFIGS = [
#     {
#         'base_url': 'http://127.0.0.1:8000',
#         'request': {
#             'auth': 'api-reader:MyPass39dza2es',
#         },
#         'models': [
#             {'url': '/api/v1/contact-list/',
#              'app': 'contacts_replica1',
#              'model': 'contact'},
#             {'url': '/api/v1/comment-list/',
#              'app': 'contacts_replica1',
#              'model': 'comment'},
#         ],
#     }
# ]

# SQL EXPLORER
EXPLORER_CONNECTIONS = {'Default': 'default'}
EXPLORER_DEFAULT_CONNECTION = 'default'
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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',

    '_project_',

    # APPS
    'contacts',

    # HISTORY
    'simple_history',

    # API
    'cors',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_filters',
    'django_filters',
    'crispy_forms',  # sexy django_filters forms
    'drf_yasg',

    # LIB
    'lib.codegen',
    'lib.integra',

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

    # APM
    'ddtrace.contrib.django',
    'elasticapm.contrib.django',

    'bootstrapform',  # sexy form in _project_/templates

    # DEV
    'debug_toolbar',
    'django_extensions',
    'explorer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'cors.middleware.CachedCorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # HISTORY
    'simple_history.middleware.HistoryRequestMiddleware',

    # DEV
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # APM
    'elasticapm.contrib.django.middleware.TracingMiddleware',
]

# CORS
CORS_ORIGIN_WHITELIST = os.environ.get('CORS_ORIGIN_WHITELIST', '').split()
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r'^/(api|openid).*$'
CORS_MODEL = 'cors.Cors'

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
        engine='django.contrib.gis.db.backends.postgis'
    )
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": SERVICE_NAME
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
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

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

MEDIA_URL = '/media/'
# TODO(GregEremeev) MEDIUM: At this moment, we use a common gCloud
# storage for all services. That's why we need to use some service specific
# path prefix(MEDIA_ROOT_PROJECT_PATH_PREFIX)
# to share the storage with all services without collisions
MEDIA_ROOT_PROJECT_PATH_PREFIX = os.environ.get('SERVICE_NAME', 'boilerplate')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(DATA_DIR, 'media'))

PRIVATE_STORAGE_ROOT = os.path.join(DATA_DIR, f'{SERVICE_NAME}_private')
PRIVATE_STORAGE = FileSystemStorage(location=PRIVATE_STORAGE_ROOT)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

LOGIN_REDIRECT_URL = '/'
INDEX_STAFF_REDIRECT_URL = '/admin/'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'core.ldap.RemoteUserBackend',
]

# Celery
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_IMPORTS = [
    'core.tasks',
]
CELERYBEAT_SCHEDULE_FILENAME = os.path.join(DATA_DIR, 'celerybeat.db')
CELERYBEAT_SCHEDULE = {}

# API
ALLOWED_APPS_FOR_PERMISSIONS_VIEW = {'auth', 'contacts'}

# DRF
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
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'core.api.permissions.DjangoModelViewPermission',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (),
    'DEFAULT_CONTENT_NEGOTIATION_CLASS':
        'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.URLPathVersioning',

    # Generic view behavior
    'DEFAULT_PAGINATION_CLASS': 'core.api.pagination.StandardizedPagination',
    # TODO: use: StandardizedFieldFilters, StandardizedSearchFilter,
    # StandardizedOrderingFilter as default filter backends
    'DEFAULT_FILTER_BACKENDS': (),

    'EXCEPTION_HANDLER': 'core.api.exception_handler.standardized_handler',

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# SCHEMA
SWAGGER_SETTINGS = {
    'DEFAULT_GENERATOR_CLASS': 'core.api.schema.StandardizedSchemaGenerator',
    'DEFAULT_AUTO_SCHEMA_CLASS': 'core.api.schema.StandardizedAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.RecursiveFieldInspector',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.HiddenFieldInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'DEFAULT_FILTER_INSPECTORS': [
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'core.api.inspectors.StandardizedPaginationInspector',
        'drf_yasg.inspectors.DjangoRestResponsePagination',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_API_URL': None,
    'DEFAULT_INFO': '_project_.swagger.INFO',
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    },
    'SECURITY_REQUIREMENTS': None,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'patch',
        'delete',
        'options',
    ],
    'DISPLAY_OPERATION_ID': False,
}

# storage
FILE_STORAGE_BACKEND = os.environ.get('FILE_STORAGE_BACKEND', 'local')
if FILE_STORAGE_BACKEND == 'gcloud':
    from google.oauth2 import service_account  # noqa
    _CREDENTIALS = os.environ['FILE_STORAGE_BACKEND_CREDENTIALS']
    GS_BUCKET_NAME = os.environ['FILE_STORAGE_BUCKET_NAME']
    GS_PROJECT_ID = os.environ['FILE_STORAGE_PROJECT_ID']
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
        json.loads(base64.b64decode(_CREDENTIALS), strict=False))
    GS_EXPIRATION = os.environ.get(
        'FILE_STORAGE_EXPIRATION_SECONDS', timedelta(seconds=7200))
    GS_FILE_OVERWRITE = False
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
else:
    logging.warning('!! DEFAULT_FILE_STORAGE="FileSystemStorage"')
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE = os.environ.get(
    'ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE', 1)
SOFT_DELETE_SAFE_MODE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '[django] %(levelname)s %(asctime)s %(name)s/%(module)s %(process)d/%(thread)d: %(message)s'  # noqa
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  # noqa
            'tags': {'environment': ENVIRONMENT},
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
        'raven': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}


try:
    from .settings_local import *  # noqa: pylint=unused-wildcard-import, pylint=wildcard-import
except ImportError:
    pass


from lib.oidc_relied.settings import set_oidc_settings  # noqa: pylint=wrong-import-position
set_oidc_settings(globals())
