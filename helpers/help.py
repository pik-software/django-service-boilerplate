#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function
import os

from lib import venv_activate_command, fix_sys_paths, \
    import_project_stub_settings
from lib2 import conf_from_pyfile

__author__ = 'pahaz'

if __name__ == "__main__":
    _PROJECT_STUB_SETTINGS_ = os.path.join("_project_", "stub_settings.py")

    fix_sys_paths()
    settings = conf_from_pyfile(_PROJECT_STUB_SETTINGS_)

    how_to_active = venv_activate_command(settings)

    print("""HELPER

    Make virtualenv: python helpers/mkvirtualenv.py
    Active virtualenv: {0}


    """.format(how_to_active))
