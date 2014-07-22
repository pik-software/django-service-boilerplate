#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import sys
from tempfile import NamedTemporaryFile
import os

from os.path import dirname, join, abspath


__author__ = 'pahaz'
_root = abspath(dirname(dirname(__file__)))


# ##############
#             #
#  HELPERS    #
#             #
###############

def fix_sys_paths():
    if hasattr(fix_sys_paths, "path_fixed"):
        return
    # insert stub root for import paths
    sys.path.insert(1, _root)
    setattr(fix_sys_paths, "path_fixed", True)


def import_project_stub_settings(project_name):
    settings = __import__(project_name + ".stub_settings")
    return settings.stub_settings


def is_venv_exists(settings):
    active_file = venv_script_file(settings, "activate")
    return os.path.exists(active_file)


def venv_pip_file(settings):
    return venv_script_file(settings, 'pip')


def venv_python_file(settings):
    return venv_script_file(settings, 'python')


def venv_script_file(settings, filename):
    bin_ = 'Scripts' if sys.platform == 'win32' else 'bin'
    return join(settings.PATH_TO_PROJECT_VENV_DIR, bin_, filename)


def venv_activate_command(settings):
    active = venv_script_file(settings, "activate")
    active = active if sys.platform == 'win32' else 'source ' + active
    return active


def pip_install(pip, requirements_file, use_cache=True, cache_dir=None):
    command = [pip, 'install']
    if use_cache:
        if not cache_dir:
            cache_dir = join(_root, '..', '.pip_cache')
        command.append('--download-cache={0}'.format(cache_dir))
    command.extend(['-r', requirements_file])
    subprocess.call(command)


def separate_requirements(settings):
    req_file = settings.PATH_TO_PROJECT_REQUIREMENTS_FILE
    common_req = []
    dev_req = []
    with open(req_file, 'r') as f:
        reqs = iter(f.readlines())
        for x in reqs:
            if x.upper().startswith("# DEV"):
                dev_req.append(x)
                break
            common_req.append(x)

        for x in reqs:
            dev_req.append(x)
    return {'common': common_req, 'dev': dev_req}


def separate_requirements_as_files(settings):
    req = separate_requirements(settings)
    req_common = ''.join(req['common'])
    req_dev = ''.join(req['dev'])
    req_common_file = make_temp_file(req_common)
    req_dev_file = make_temp_file(req_dev)
    return {'common': req_common_file, 'dev': req_dev_file,
            'common_content': req_common, 'dev_content': req_dev}


def make_temp_file(content):
    common = NamedTemporaryFile('w', delete=False)
    common.write(content)
    common.close()
    return common.name


def root_join(*args):
    return join(_root, *args)

###############
#             #
#    MAIN     #
#             #
###############

if __name__ == "__main__":
    PROJECT_DIR_NAME = "_project_"
    PRODUCTION_MODE = False
    USE_PIP_CACHE = True
    USE_FIXES = True

    if '--production' in sys.argv:
        PRODUCTION_MODE = True
    if '--no-use-pip-cache' in sys.argv:
        USE_PIP_CACHE = False
    if '--no-use-fixes' in sys.argv:
        USE_FIXES = False

    fix_sys_paths()
    s = import_project_stub_settings(PROJECT_DIR_NAME)

    print("\nMAKE VIRTUALENV\n")
    subprocess.call(['virtualenv', s.PATH_TO_PROJECT_VENV_DIR])

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
