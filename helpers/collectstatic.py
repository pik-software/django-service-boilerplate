#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function
import subprocess

from _settings import settings, root_join
from lib import is_venv_exists, venv_python_file

__author__ = 'pahaz'

if __name__ == "__main__":
    is_venv_exists = is_venv_exists(settings)
    python = venv_python_file(settings) if is_venv_exists else 'python'
    print("CALL `collectstatic` (python={0})".format(python))
    subprocess.call([
        python,
        root_join('manage.py'),
        'collectstatic',
        '--noinput'])
