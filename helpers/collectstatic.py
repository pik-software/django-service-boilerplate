#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import subprocess

from .lib import fix_sys_paths, import_project_stub_settings, \
    root_join, venv_python_file, is_venv_exists

__author__ = 'pahaz'

if __name__ == "__main__":
    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    settings = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    is_venv_exists = is_venv_exists(settings)
    python = venv_python_file(settings) if is_venv_exists else 'python'
    print("CALL `collectstatic` (python={0})".format(python))
    subprocess.call([python, root_join('manage.py'), 'collectstatic', '--noinput'])
