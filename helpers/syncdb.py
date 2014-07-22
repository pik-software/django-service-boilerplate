from __future__ import unicode_literals
from __future__ import print_function
import subprocess

import os
from mkvirtualenv import fix_sys_paths, import_project_stub_settings, \
    root_join, venv_python_file, is_venv_exists


__author__ = 'pahaz'

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"
    DELETE_DB_IF_EXISTS = True

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    is_db_exists = os.path.exists(settings.PATH_TO_PROJECT_SQLITE_FILE)
    if is_db_exists and DELETE_DB_IF_EXISTS:
        print("REMOVE EXISTS SQLITE_FILE")
        os.remove(settings.PATH_TO_PROJECT_SQLITE_FILE)

    is_venv_exists = is_venv_exists(settings)
    python = venv_python_file(settings) if is_venv_exists else 'python'
    print("CALL `syncdb` (python={0})".format(python))
    subprocess.call([python, root_join('manage.py'), 'syncdb', '--noinput'])
