import sys
import shutil

from os.path import join, dirname, abspath
import os
import stat


__author__ = 'pahaz'
_root = abspath(dirname(__file__))
_git_url = "https://github.com/pahaz/django-project-stub.git"


def stub_dir_for_tests():
    return join(_root, '.test', 'project-name')


def venv_activate_command():
    bin_ = 'Scripts' if sys.platform == 'win32' else 'bin'
    active = (join(stub_dir_for_tests(), '__data__', 'venv', bin_, 'activate'))
    return active if sys.platform == 'win32' else 'source ' + active


def venv_python_bin():
    bin_ = 'Scripts' if sys.platform == 'win32' else 'bin'
    return join(stub_dir_for_tests(), '__data__', 'venv', bin_, 'python')


print("CWD: " + _root)
os.chdir(_root)
tests_dir = join(_root, '.test')
if not os.path.exists(tests_dir):
    print("#!# MKDIR .test")
    os.mkdir(tests_dir)


def rm_rf(path):
    if not os.path.exists(path):
        return

    def _on_rm_error(func, path, exc_info):
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
system('git clone {0} project-name'.format(_git_url))
os.chdir('project-name')
system('python setup.py')
system('python helpers/mkvirtualenv.py')
system('{py} manage.py syncdb --noinput'.format(py=venv_python_bin()))

print("OK!")
