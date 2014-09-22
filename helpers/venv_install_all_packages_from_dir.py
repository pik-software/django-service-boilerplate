#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import sys
import subprocess
import os
from os.path import join, dirname

from lib import venv_pip_file, fix_sys_paths, \
    import_project_stub_settings, root_join
from lib2 import conf_from_pyfile

__author__ = 'pahaz'

if __name__ == "__main__":
    PACKAGES_DIR = root_join('..', ".pip_cache")

    if len(sys.argv) >= 2:
        PACKAGES_DIR = sys.argv[1]

    _PROJECT_STUB_SETTINGS_ = os.path.join("_project_", "stub_settings.py")

    fix_sys_paths()
    settings = conf_from_pyfile(_PROJECT_STUB_SETTINGS_)

    for x in os.listdir(PACKAGES_DIR):
        if x.endswith("content-type"):
            continue
        file_ = join(PACKAGES_DIR, x)
        cmd = [venv_pip_file(settings), "install", "--no-deps", file_]
        print(' '.join(cmd))
        subprocess.call(cmd)
