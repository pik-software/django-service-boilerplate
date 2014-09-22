#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function
import os

import subprocess
import sys

from lib import fix_sys_paths, import_project_stub_settings, \
    venv_script_file, separate_requirements, make_temp_file, venv_pip_file, \
    pip_install, venv_activate_command
from lib2 import conf_from_pyfile

__author__ = 'pahaz'


def python_version(number):
    if number not in [2, 3]:
        raise RuntimeError('Only 2 or 3 python version support.')

    if sys.platform == 'win32':
        return 'python3.exe' if number == 3 else 'python.exe'
    else:
        return 'python3' if number == 3 else 'python2'


if __name__ == "__main__":
    PRODUCTION_MODE = False
    USE_PIP_CACHE = True
    USE_FIXES = False
    PY_VERSION = 3

    if '--production' in sys.argv:
        PRODUCTION_MODE = True
    if '--no-use-pip-cache' in sys.argv:
        USE_PIP_CACHE = False
    if '--no-use-fixes' in sys.argv:
        USE_FIXES = False

    _PROJECT_STUB_SETTINGS_ = os.path.join("_project_", "stub_settings.py")

    fix_sys_paths()
    s = conf_from_pyfile(_PROJECT_STUB_SETTINGS_)

    print("\nMAKE VIRTUALENV\n")
    subprocess.call(['virtualenv', '--python=' + python_version(PY_VERSION),
                     '--no-site-packages', s.PATH_TO_PROJECT_VENV_DIR])

    if USE_FIXES and sys.platform == 'win32':
        print("\nINSTALL PIL [hotfix for windows]\n")
        easy_install = venv_script_file(s, 'easy_install')
        subprocess.call([easy_install, 'PIL'])

    print("\nINSTALL REQUIREMENTS\n")
    req = separate_requirements(s)
    common_req = req['common']
    dev_req = req['dev']

    print("\n# ! #\n# COMMON requirements:\n\n\n" + ''.join(common_req))
    print("\n# ! #\n# DEV requirements:\n\n\n" + ''.join(dev_req))

    common = make_temp_file(''.join(common_req))
    dev = make_temp_file(''.join(dev_req))

    pip = venv_pip_file(s)
    print("""
     # COMMON #
     """)
    pip_install(pip, common, USE_PIP_CACHE)
    if not PRODUCTION_MODE:
        print("""
     # DEV #
     """)
        pip_install(pip, dev, USE_PIP_CACHE)

    print("""NOW ACTIVATE:
     * {help_activate_venv}
    """.format(help_activate_venv=venv_activate_command(s)))
