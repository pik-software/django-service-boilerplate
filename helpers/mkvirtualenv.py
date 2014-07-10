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
BASE_DIR = dirname(dirname(__file__))


#################
#               #
#  PYTHON PATH  #
#               #
#################

# insert stub root for import paths
sys.path.insert(1, BASE_DIR)


###############
#             #
#  HELPERS    #
#             #
###############


def import_project_stub_settings(project_name):
    settings = __import__(project_name + ".settings.global_stub_settings")
    return settings


def pip_file(settings):
    return venv_script_file(settings, 'pip')


def venv_script_file(settings, filename):
    bin = 'Scripts' if sys.platform == 'win32' else 'bin'
    return join(settings.PATH_TO_VENV_DIR, bin, filename)


###############
#             #
#    MAIN     #
#             #
###############

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"
    PRODUCTION_MODE = False

    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    print("MAKE VIRTUALENV")
    subprocess.call(['virtualenv', settings.PATH_TO_VENV_DIR])

    print("INSTALL REQUIREMENTS")
    req_dir = join(BASE_DIR, '_project_', 'requirements')
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
