#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

from _settings import settings
from lib import mkdir_if_not_exists

__author__ = 'pahaz'


def make_all_required_dirs(settings):
    mkdir_if_not_exists(settings.PATH_TO_PROJECT_VENV_DIR)
    mkdir_if_not_exists(settings.PATH_TO_PROJECT_LOG_DIR)
    mkdir_if_not_exists(settings.PATH_TO_PROJECT_MEDIA_DIR)
    mkdir_if_not_exists(settings.PATH_TO_PROJECT_TMP_DIR)
    mkdir_if_not_exists(settings.PATH_TO_PROJECT_DATA_DIR)


if __name__ == "__main__":
    make_all_required_dirs(settings)