[![Build Status](https://travis-ci.org/pahaz/django-project-stub.svg?branch=master)](https://travis-ci.org/pahaz/django-project-stub)

# HowTo Use #

Backend requirements:

  1. install `pip` -- https://pip.pypa.io/en/stable/installing/#installation
  1. install `virtualenv` -- https://virtualenv.pypa.io/en/stable/installation/#installation
  1. install `virtualenvwrapper` -- https://virtualenvwrapper.readthedocs.io/en/latest/install.html#installation (`pip install virtualenvwrapper`)
  1. install and run `PostgreSQL` and `Redis`
  1. install `PhantomJS` selenium driver (if you want to run selenium tests)

Frontend requirements:

  1. install `bower` -- https://bower.io/#install-bower (install `npm`, `node`, run `npm install -g bower`)

Ubuntu OS:
1. install `libcurl4-openssl-dev` -- https://packages.ubuntu.com/xenial/libcurl4-openssl-dev (`sudo apt-get install libcurl4-openssl-dev`)
1. install `zlib1g-dev` -- https://packages.ubuntu.com/ru/xenial/zlib1g-dev (`sudo apt-get install zlib1g-dev`)
1. install `postgis` -- http://postgis.net/install/ (`sudo apt-get install postgis`)
1. install `libgdal-dev` -- https://packages.ubuntu.com/xenial/libgdal-dev (`sudo apt-get install libgdal-dev`)
1. install `gdal` -- https://pypi.python.org/pypi/GDAL (`pip install gdal`)

Create new project, virtualenv and install requirements:

    git clone git@github.com:pik-software/<repo>.git <project-name>
    cd <project-name>
    mkvirtualenv --python=$(which python3.5) <project-name>
    pip install -r requirements.txt  # install python requirements

Create file `settings_local.py` in `_project_` and setup DATABASE and some local settings:

      DEBUG = True
      SECRET_KEY = '0n-w7wsf^3-ehi^!@m2fayppf7cc3k4j5$2($59ai*5whm^l7k'
      DATABASES = {
          'default': {
              'ENGINE': 'django.contrib.gis.db.backends.postgis',
              'NAME': '<project-name>',
              'USER': 'postgres',
              'PASSWORD': 'postgres',
              'HOST': 'localhost',
              'PORT': '5432'
          }
      }

Create and migrate database:

    createdb <project-name>  # create postgres database
    (OR sudo su postgres -c "createdb <project-name>")
    python manage.py migrate

Run dev server:

    python manage.py runserver

Database transfer with dumpfile:

    # The command for create dumpfile (on localhost)
    pg_dump -d <project-name> -h localhost -U postgres -W -Fc -x -O > dump.dmp

    # The command for restore dump from file (on server)
    pg_restore dump.dmp
