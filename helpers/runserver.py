from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import os

from mkvirtualenv import help_activate_venv_command, fix_sys_paths, \
    import_project_stub_settings, venv_script_file, root_join


__author__ = 'pahaz'

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"

    fix_sys_paths()
    settings = import_project_stub_settings(PROJECT_DIR_NAME)

    how_to_active = help_activate_venv_command(settings)


    is_venv_exists = os.path.exists(how_to_active)
    py = venv_script_file(settings, 'python') if is_venv_exists else 'python'
    print("CALL `runserver` (python={0})".format(py))
    subprocess.call([py, root_join('manage.py'), 'runserver'])
