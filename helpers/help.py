#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function

from mkvirtualenv import help_activate_venv_command, fix_sys_paths, \
    import_project_stub_settings


###############
#             #
#  VARIABLES  #
#             #
###############

__author__ = 'pahaz'
PROJECT_DIR_NAME = "_project_"
PRODUCTION_MODE = False

fix_sys_paths()
settings = import_project_stub_settings(PROJECT_DIR_NAME)

how_to_active = help_activate_venv_command(settings)

print("""HELPER

Make virtualenv: python helpers/mkvirtualenv.py
Active virtualenv: {0}


""".format(how_to_active))