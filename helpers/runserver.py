from __future__ import unicode_literals
from __future__ import print_function
import subprocess

from mkvirtualenv import fix_sys_paths, import_project_stub_settings, \
    root_join, venv_python_file, is_venv_exists


__author__ = 'pahaz'

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    is_venv_exists = is_venv_exists(settings)
    python = venv_python_file(settings) if is_venv_exists else 'python'
    print("CALL `runserver` (python={0})".format(python))
    subprocess.call([python, root_join('manage.py'), 'runserver'])
