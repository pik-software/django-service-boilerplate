![build](https://travis-ci.org/pahaz/django-project-stub.svg)

# Project structure #

Conventions: 
 * only one project (site) for this stab. (if you can use many sites, see `EXT1` or report issue)
 * if project contain a cool app with may be uses in other projects (sites) you must move this app to special repository.
And use this app as requirements.
 * support Django>=1.6.5
 * use PyCharm IDE


 - [dir] `__data__` - project workflow data: `venv`, `media`, `db` (see: __data__/README.md)
 - [dir] `_project_` - project level settings and files
    - [dir] `/templates` - project level templates (and for override templates)
    - [dir] `/settings` - project `settings.py` with sections support (see: _project_/settings/__init__.py)
    - [dir] `/fixtures` - project level fixtures
    - [dir] `/static` - project level static files (JS, CSS, IMAGES, ...)
    - [file] `/urls.py` - project level routs
    - [file] `/requirements.txt` - project level requirements (production, development); file contain two sections: 1) only production requirements 2) additional packages for development/testing
    - [file] `/global_stub_settings.py` - project workflow data settings
 - [file] `manage.py` - django manage commands
 - [file] `setup.py` - set up new project

# HowTo Use #

    # require!
    easy_install -U pip
    easy_install -U virtualenv

    # create project-name!
    git clone https://github.com/pahaz/django-project-stub.git project-name
    cd project-name
    python setup.py

# Test #

OS: Windows/Linux
Python: 2.7/3.3
