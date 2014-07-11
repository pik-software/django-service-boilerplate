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


def vpython_bin():
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    py = join(_root, '__data__', 'venv', bin, 'python')
    return py


tests_dir = join(_root, '.test')
if not os.path.exists(tests_dir):
    print("#!# os.mkdir! .test")
    os.mkdir(tests_dir)

exec_file = join(_root, '.test', 'go.sh.cmd')
f = open(exec_file, 'w')
f.write("""#!/bin/bash
pushd "%~dp0"
rm -rf project-name
git clone https://github.com/pahaz/django-project-stub.git project-name
cd project-name
python setup.py
python helpers/mkvirtualenv.py
{vpython_bin} manage.py syncdb --noinput
{vpython_bin} manage.py runserver
popd
""".format(
    venv_activate_command=venv_activate_command(),
    vpython_bin=vpython_bin(),
))
f.close()

print(exec_file)
subprocess.call([exec_file])