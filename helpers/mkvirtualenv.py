#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import sys
from os.path import dirname, join


###############
#             #
#  VARIABLES  #
#             #
###############

__author__ = 'pahaz'
_project_root = dirname(dirname(__file__))


###############
#             #
#  HELPERS    #
#             #
###############

def fix_sys_paths():
    if hasattr(fix_sys_paths, "path_fixed"):
        return
    # insert stub root for import paths
    sys.path.insert(1, _project_root)
    setattr(fix_sys_paths, "path_fixed", True)


def import_project_stub_settings(project_name):
    settings = __import__(project_name + ".global_stub_settings")
    return settings.global_stub_settings


def pip_file(settings):
    return venv_script_file(settings, 'pip')


def venv_script_file(settings, filename):
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    return join(settings.PATH_TO_VENV_DIR, bin, filename)


def help_activate_venv_command(settings):
    active = venv_script_file(settings, "activate")
    active = active if sys.platform == 'win32' else 'source ' + active
    return active

###############
#             #
#    MAIN     #
#             #
###############

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"
    PRODUCTION_MODE = False

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    print("MAKE VIRTUALENV")
    subprocess.call(['virtualenv', settings.PATH_TO_VENV_DIR])

    print("INSTALL REQUIREMENTS")
    req_dir = join(_project_root, '_project_', 'requirements')
    req_common = join(req_dir, 'common_requirements.txt')
    req_dev = join(req_dir, 'development_requirements.txt')
    req_prod = join(req_dir, 'production_requirements.txt')
    print(" * common ")
    subprocess.call([pip_file(settings), 'install', '-r', req_common])
    if PRODUCTION_MODE:
        print(" * production ")
        subprocess.call([pip_file(settings), 'install', '-r', req_prod])
    else:
        print(" * development ")
        subprocess.call([pip_file(settings), 'install', '-r', req_dev])

    active = help_activate_venv_command(settings)
    print("""NOW ACTIVATE:
     * {0}
    """.format(active))
