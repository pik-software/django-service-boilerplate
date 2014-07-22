#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function
import sys
import subprocess

import os
from os.path import join, dirname
from mkvirtualenv import venv_pip_file, fix_sys_paths, \
    import_project_stub_settings


__author__ = 'pahaz'
_root = dirname(dirname(__file__))


if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"
    PACKAGES_DIR = join(_root, '..', ".pip_cache")

    if len(sys.argv) >= 2:
        PACKAGES_DIR = sys.argv[1]

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    for x in os.listdir(PACKAGES_DIR):
        if x.endswith("content-type"):
            continue
        file_ = join(PACKAGES_DIR, x)
        cmd = [venv_pip_file(settings), "install", "--no-deps", file_]
        print(' '.join(cmd))
        subprocess.call(cmd)
