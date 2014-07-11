from os.path import join, dirname
import sys
import os
import subprocess

__author__ = 'pahaz'
_root = dirname(__file__)


def venv_activate_command():
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    active = join(_root, '__data__', 'venv', bin, 'activate')
    return active if sys.platform == 'win32' else 'source ' + active


if not os.path.exists('.test'):
    os.mkdir('mkdir .test')

exec_file = join(_root, '.test', 'go.sh.cmd')

f = open(exec_file, 'w')
f.write("""#!/bin/bash
pushd "%~dp0"
rm -rf project-name
git clone https://github.com/pahaz/django-project-stub.git project-name
cd project-name
python setup.py
python helpers/mkvirtualenv.py
{venv_activate_command}
python manage.py syncdb --noinput
python manage.py runserver
popd
""".format(venv_activate_command=venv_activate_command()))
f.close()

print(exec_file)
subprocess.call([exec_file])