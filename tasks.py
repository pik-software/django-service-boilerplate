import os

from invoke import run, task

from _project_.settings import DATA_DIR, STATIC_ROOT, MEDIA_ROOT, PROJECT_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_LOCAL_SETTINGS = os.path.join(PROJECT_DIR, 'settings_local.py')
FRONTEND_BOWER_JSON = os.path.join(BASE_DIR, 'bower.json')


@task
def init(ctx):
    _mkdir(DATA_DIR)
    _mkdir(STATIC_ROOT)
    _mkdir(MEDIA_ROOT)
    _mkvenv()
    run_in_venv('pip install -r requirements.txt')
    if not os.path.exists(PROJECT_LOCAL_SETTINGS):
        _mkfile(PROJECT_LOCAL_SETTINGS, '')
    migrate(ctx)

    if os.path.exists(FRONTEND_BOWER_JSON):
        run('bower install')

    print("Use: `workon '%s'` for venv activation" % _get_venv_name())


@task
def runserver(ctx):
    run_in_venv('python manage.py runserver')


@task
def migrate(ctx):
    run_in_venv('python manage.py migrate -v1')


def run_in_venv(command):
    kwargs = {'echo': True}
    if os.name != 'nt':
        kwargs['pty'] = True
    run(_venv_activate_wrap(command), **kwargs)


def _mkdir(path):
    if not os.path.exists(path):
        _mkdir(os.path.dirname(path))
        os.mkdir(path)


def _mkfile(path, content):
    with open(path, 'w') as f:
        f.write(content)


def _cat(path):
    with open(path, 'r') as f:
        return f.read()


def _mkvenv():
    venv_name_path = os.path.join(BASE_DIR, '.venv')
    if not os.path.exists(venv_name_path):
        venv_name = os.path.basename(BASE_DIR)
        run('mkvirtualenv --python=python3.5 "%s"' % venv_name)
        _mkfile(venv_name_path, venv_name)


def _get_venv_name():
    venv_name_path = os.path.join(BASE_DIR, '.venv')
    if not os.path.exists(venv_name_path):
        return None
    return _cat(venv_name_path).strip()


def _venv_activate_wrap(cmd):
    venv_name = _get_venv_name()
    if not venv_name:
        raise RuntimeError('Invalid virtualenv name. Make sure that .venv '
                           'file exists and contains virtualenv name')
    return ". virtualenvwrapper.sh && workon '%s' && (%s)" % (venv_name, cmd)
