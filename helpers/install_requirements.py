#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function

from lib import fix_sys_paths, import_project_stub_settings, \
    pip_install, separate_requirements_as_files, is_venv_exists, venv_pip_file


__author__ = 'pahaz'

if __name__ == "__main__":
    PRODUCTION_MODE = False
    USE_PIP_CACHE = True
    _PROJECT_STUB_SETTINGS_ = "_project_.stub_settings"

    fix_sys_paths()
    settings = import_project_stub_settings(_PROJECT_STUB_SETTINGS_)

    req = separate_requirements_as_files(settings)

    is_venv_exists = is_venv_exists(settings)
    pip = venv_pip_file(settings) if is_venv_exists else 'pip'

    print("CALL `pip install` (pip=`{0}`)".format(pip))
    print("INSTALL COMMON ({0})".format(req['common']))
    pip_install(pip, req['common'], USE_PIP_CACHE)
    if not PRODUCTION_MODE:
        print("INSTALL DEV ({0})".format(req['dev']))
        pip_install(pip, req['dev'], USE_PIP_CACHE)
