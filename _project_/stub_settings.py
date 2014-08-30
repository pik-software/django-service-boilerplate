# coding=utf-8
from os.path import dirname, join, basename, abspath

# IF you change variables name please update version variable.
_stub_settings_version_ = '0.0.1'

ROOT_DIR = abspath(dirname(dirname(__file__)))
ROOT_DIR_NAME = basename(ROOT_DIR)

PROJECT_DIR = dirname(__file__)
PROJECT_DIR_NAME = basename(PROJECT_DIR)

PATH_TO_PROJECT_VENV_DIR = join(ROOT_DIR, '__data__', 'venv')
PATH_TO_PROJECT_LOG_DIR = join(ROOT_DIR, '__data__', 'log')
PATH_TO_PROJECT_COLLECT_STATIC_DIR = \
    join(ROOT_DIR, '__data__', 'collected_static')
PATH_TO_PROJECT_MEDIA_DIR = join(ROOT_DIR, '__data__', 'media')
PATH_TO_PROJECT_TMP_DIR = join(ROOT_DIR, '__data__', 'tmp')
PATH_TO_PROJECT_SQLITE_FILE = join(ROOT_DIR, '__data__', 'db.sqlite')
PATH_TO_PROJECT_REQUIREMENTS_FILE = join(ROOT_DIR, 'requirements.txt')

PATH_TO_PROJECT_DATA_DIR = join(ROOT_DIR, '__data__')
