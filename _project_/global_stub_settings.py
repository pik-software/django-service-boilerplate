from os.path import dirname, join, basename

PROJECT_ROOT = dirname(dirname(dirname(__file__)))
PROJECT_DIRNAME = basename(PROJECT_ROOT)

PATH_TO_VENV_DIR = join(PROJECT_ROOT, '__data__', 'venv')
PATH_TO_COLLECT_STATIC_DIR = join(PROJECT_ROOT, '__data__', 'collected_static')
PATH_TO_MEDIA_DIR = join(PROJECT_ROOT, '__data__', 'media')
PATH_TO_SQLITE_FILE = join(PROJECT_ROOT, '__data__', 'db.sqlite')
