#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

from _settings import settings
from lib import venv_activate_command

__author__ = 'pahaz'

if __name__ == "__main__":
    how_to_active = venv_activate_command(settings)

    print("""HELPER

    Make folders structure: python helpers/mkfolders.py
    Make virtualenv: python helpers/mkvirtualenv.py
    Active virtualenv: {0}

    Synchronize db: python helpers/syncdb.py
    Run test: python helpers/test.py
    Run dev server: python helpers/runserver.py

    """.format(how_to_active))
