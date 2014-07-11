from os.path import join, dirname, abspath
import sys
import os
import subprocess
import shutil
import stat

__author__ = 'pahaz'
_root = dirname(__file__)


def test_stub_root():
    return abspath(join(_root, '.test', 'project-name'))


def venv_activate_command():
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    active = abspath(
        join(test_stub_root(), '__data__', 'venv', bin, 'activate'))
    return active if sys.platform == 'win32' else 'source ' + active


def vpython_bin():
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    py = abspath(join(test_stub_root(), '__data__', 'venv', bin, 'python'))
    return py


os.chdir(_root)
tests_dir = join(_root, '.test')
if not os.path.exists(tests_dir):
    print("#!# MKDIR .test")
    os.mkdir(tests_dir)


def rm_rf(path):
    if not os.path.exists(path):
        return

    def _on_rm_error(func, path, exc_info):
        # path contains the path of the file that couldn't be removed
        # let's just assume that it's read-only and unlink it.
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    shutil.rmtree(path, onerror=_on_rm_error)


def system(cmd):
    cwd = os.getcwd()
    print("#!# RUN: {0} (work dir is {1})".format(cmd, cwd))
    status = os.system(cmd)
    if status != 0:
        raise Exception("#!# Bead status for CMD: " + cmd)


os.chdir(tests_dir)

rm_rf('project-name')
system(
    'git clone https://github.com/pahaz/django-project-stub.git project-name')
os.chdir('project-name')
system('python setup.py')
system('python helpers/mkvirtualenv.py')
system('{py} manage.py syncdb --noinput'.format(py=vpython_bin()))

print("OK!")

# exec_file = join(_root, '.test', 'go.sh.cmd')
# f = open(exec_file, 'w')
# f.write("""#!/bin/bash
# pushd "%~dp0"
# rm -rf project-name
# git clone https://github.com/pahaz/django-project-stub.git project-name
# cd project-name
# python setup.py
# python helpers/mkvirtualenv.py
# {vpython_bin} manage.py syncdb --noinput
# {vpython_bin} manage.py runserver
# popd
# """.format(
# venv_activate_command=venv_activate_command(),
# vpython_bin=vpython_bin(),
# ))
# f.close()
#
# print(exec_file)
#
# # mk executable
# st = os.stat(exec_file)
# os.chmod(exec_file, st.st_mode | stat.S_IEXEC)
# # execute
# subprocess.call([exec_file])