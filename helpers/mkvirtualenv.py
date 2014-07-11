#!/usr/bin/python

from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import sys
from os.path import dirname, join
from tempfile import NamedTemporaryFile


__author__ = 'pahaz'
_root = dirname(dirname(__file__))


###############
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
    settings = __import__(project_name + ".global_stub_settings")
    return settings.global_stub_settings


def pip_file(settings):
    return venv_script_file(settings, 'pip')


def venv_script_file(settings, filename):
    bin_ = 'Scripts' if sys.platform == 'win32' else 'bin'
    return join(settings.PATH_TO_PROJECT_VENV_DIR, bin_, filename)


def help_activate_venv_command(settings):
    active = venv_script_file(settings, "activate")
    active = active if sys.platform == 'win32' else 'source ' + active
    return active


def pip_install(requirements_file, use_cache=True, cache_dir=None):
    command = [pip_file(s), 'install']
    if use_cache:
        if not cache_dir:
            cache_dir = join(_root, '..', '.pip_cache')
        command.append('--download-cache={0}'.format(cache_dir))
    command.extend(['-r', requirements_file])
    subprocess.call(command)


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

    fix_sys_paths()
    s = import_project_stub_settings(PROJECT_DIR_NAME)

    print("\nMAKE VIRTUALENV\n")
    subprocess.call(['virtualenv', s.PATH_TO_PROJECT_VENV_DIR])

    if USE_FIXES and sys.platform == 'win32':
        print("\nINSTALL PIL [hotfix for windows]\n")
        easy_install = venv_script_file(s, 'easy_install')
        subprocess.call([easy_install, 'PIL'])

    print("\nINSTALL REQUIREMENTS\n")
    req_file = s.PATH_TO_PROJECT_REQUIREMENTS_FILE
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

    print("\n# ! #\n# COMMON requirements:\n\n\n" + ''.join(common_req))
    print("\n# ! #\n# DEV requirements:\n\n\n" + ''.join(dev_req))

    common = NamedTemporaryFile('w', delete=False)
    common.write(''.join(common_req))
    common.close()

    dev = NamedTemporaryFile('w', delete=False)
    dev.write(''.join(dev_req))
    dev.close()

    print("""
     # COMMON #
     """)
    pip_install(common.name, USE_PIP_CACHE)
    if not PRODUCTION_MODE:
        print("""
     # DEV #
     """)
        pip_install(dev.name, USE_PIP_CACHE)

    print("""NOW ACTIVATE:
     * {0}
    """.format(help_activate_venv=help_activate_venv_command(s)))
