#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import os

from .lib import fix_sys_paths, import_project_stub_settings, \
    make_dir_if_not_exists

__author__ = 'pahaz'


def make_all_required_dirs(settings):
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_VENV_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_LOG_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_COLLECT_STATIC_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_MEDIA_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_TMP_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_DATA_DIR)
    make_dir_if_not_exists(os.path.dirname(settings.PATH_TO_PROJECT_SQLITE_FILE))
    make_dir_if_not_exists(os.path.dirname(settings.PATH_TO_PROJECT_REQUIREMENTS_FILE))


if __name__ == "__main__":
    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    settings = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    make_all_required_dirs(settings)