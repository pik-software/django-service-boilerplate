[![Build Status](https://travis-ci.org/pahaz/django-project-stub.svg?branch=master)](https://travis-ci.org/pahaz/django-project-stub)

![index](./docs/img/index.png)

# HowTo Use #

Backend requirements:

  1. install `pip` -- https://pip.pypa.io/en/stable/installing/#installation
  1. install `virtualenv` -- https://virtualenv.pypa.io/en/stable/installation/#installation
  1. install `virtualenvwrapper` -- https://virtualenvwrapper.readthedocs.io/en/latest/install.html#installation (`pip install virtualenvwrapper`)
  1. install and run `PostgreSQL` and `Redis`
  1. install `PhantomJS` selenium driver (if you want to run selenium tests)

Frontend requirements:

  1. install `bower` -- https://bower.io/#install-bower (install `npm`, `node`, run `npm install -g bower`)

Create new project:

    git clone https://github.com/pahaz/django-project-stub.git project-name
    cd project-name
    mkvirtualenv --python=python3.5 project-name  # create virtualenv
    pip install -r requirements.txt  # install python requirements
    bower install  # install frontend requirements
    createdb project-name  # create postgres database

# Project structure #

 - [dir] `__data__` - project media data (`media` files, `db` files, `cache`, etc)
 - [dir] `_project_` - project level files
    - [dir] `./templates` - project common templates
    - [dir] `./static` - project common static files (js, css, img, etc)
    - [file] `./settings.py` - project settings
    - [file] `./urls.py` - project routs
 - [file] `requirements.txt` - project requirements
 - [file] `manage.py` - django manage file

# Tested #

OS: Windows/MacOS/Linux
Python: 3.5
