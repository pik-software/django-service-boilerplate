#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

import subprocess
import os

from _settings import settings, root_join
from lib import is_venv_exists, venv_python_file

__author__ = 'pahaz'

if __name__ == "__main__":
    DELETE_DB_IF_EXISTS = False

    is_db_exists = os.path.exists(settings.PATH_TO_PROJECT_SQLITE_FILE)
    if is_db_exists and DELETE_DB_IF_EXISTS:
        print("REMOVE EXISTS SQLITE_FILE")
        os.remove(settings.PATH_TO_PROJECT_SQLITE_FILE)

    is_venv_exists = is_venv_exists(settings)
    python = venv_python_file(settings) if is_venv_exists else 'python'
    print("CALL `migrate` (python={0})".format(python))
    subprocess.call([
        python,
        root_join('manage.py'),
        'migrate',
        '--noinput'])
