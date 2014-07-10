from os.path import dirname, join

BASE_DIR = dirname(dirname(dirname(__file__)))

PATH_TO_VENV_DIR = join(BASE_DIR, '__data__', 'venv')
PATH_TO_COLLECT_STATIC_DIR = join(BASE_DIR, '__data__', 'collected_static')
PATH_TO_MEDIA_DIR = join(BASE_DIR, '__data__', 'media')
PATH_TO_SQLITE_FILE = join(BASE_DIR, '__data__', 'db.sqlite')
