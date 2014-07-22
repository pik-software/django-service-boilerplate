#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function

from mkvirtualenv import venv_activate_command, fix_sys_paths, \
    import_project_stub_settings

__author__ = 'pahaz'

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    how_to_active = venv_activate_command(settings)

    print("""HELPER

    Make virtualenv: python helpers/mkvirtualenv.py
    Active virtualenv: {0}


    """.format(how_to_active))
