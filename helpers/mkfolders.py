#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import os

from lib import fix_sys_paths, import_project_stub_settings, \
    make_dir_if_not_exists
from lib2 import conf_from_pyfile

__author__ = 'pahaz'


def make_all_required_dirs(settings):
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_VENV_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_LOG_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_MEDIA_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_TMP_DIR)
    make_dir_if_not_exists(settings.PATH_TO_PROJECT_DATA_DIR)


if __name__ == "__main__":
    _PROJECT_STUB_SETTINGS_ = os.path.join("_project_", "stub_settings.py")

    fix_sys_paths()
    settings = conf_from_pyfile(_PROJECT_STUB_SETTINGS_)

    make_all_required_dirs(settings)