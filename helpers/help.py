#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

from lib import venv_activate_command, fix_sys_paths, \
    import_project_stub_settings


__author__ = 'pahaz'

if __name__ == "__main__":
    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    settings = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    how_to_active = venv_activate_command(settings)

    print("""HELPER

    Make virtualenv: python helpers/mkvirtualenv.py
    Active virtualenv: {0}


    """.format(how_to_active))
