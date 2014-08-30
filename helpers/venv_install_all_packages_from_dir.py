#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import sys
import subprocess
import os
from os.path import join, dirname

from .lib import venv_pip_file, fix_sys_paths, \
    import_project_stub_settings, root_join

__author__ = 'pahaz'

if __name__ == "__main__":
    PACKAGES_DIR = root_join('..', ".pip_cache")

    if len(sys.argv) >= 2:
        PACKAGES_DIR = sys.argv[1]

    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    settings = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    for x in os.listdir(PACKAGES_DIR):
        if x.endswith("content-type"):
            continue
        file_ = join(PACKAGES_DIR, x)
        cmd = [venv_pip_file(settings), "install", "--no-deps", file_]
        print(' '.join(cmd))
        subprocess.call(cmd)
