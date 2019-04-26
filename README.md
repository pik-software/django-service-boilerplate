[![CircleCI](https://circleci.com/gh/pik-software/django-service-boilerplate.svg?style=svg)](https://circleci.com/gh/pik-software/django-service-boilerplate)

# HowTo Use #

Backend requirements:

  1. install `pip` -- https://pip.pypa.io/en/stable/installing/#installation
  1. install `virtualenv` -- https://virtualenv.pypa.io/en/stable/installation/#installation
  1. install `virtualenvwrapper` -- https://virtualenvwrapper.readthedocs.io/en/latest/install.html#installation (`pip install virtualenvwrapper`)
  1. install and run `PostgreSQL` and `Redis`
  1. install `PhantomJS` selenium driver (if you want to run selenium tests)

Ubuntu OS:
1. install `libcurl4-openssl-dev` -- https://packages.ubuntu.com/xenial/libcurl4-openssl-dev (`sudo apt-get install libcurl4-openssl-dev`)
1. install `zlib1g-dev` -- https://packages.ubuntu.com/ru/xenial/zlib1g-dev (`sudo apt-get install zlib1g-dev`)
1. install `postgis` -- http://postgis.net/install/ (`sudo apt-get install postgis`)
1. install `libgdal-dev` -- https://packages.ubuntu.com/xenial/libgdal-dev (`sudo apt-get install libgdal-dev`)
1. install `gdal` -- https://pypi.python.org/pypi/GDAL (`pip install gdal`)

Create new project, virtualenv and install requirements:

    git clone git@github.com:pik-software/<repo>.git <project-name>
    cd <project-name>
    mkvirtualenv --python=$(which python3.6) <project-name>
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

Run tests:

    # Execute tests with predefined `test.ini` project settings
    
    pytest

    # WARNING! By default `--reuse-db` is on, it means that test database is 
    # saved between test sessions. To override this behaviour or in case of 
    # problems like "Permission already exists" or similar, use `--create-db` 
    # option for db recreation forcing.
    
    pytest --create-db

# ENVIRONMENTS #

`CELERY_WORKER_CONCURRENCY` -- celery worker concurrency info

# lib.codegen #

Help you to generate django models by OpenAPI Swagger schema.

1. Add `lib.codegen` to `INSTALLED_APPS`

2. run `python manage.py schema_to_models ./app.schema.json app_name` command

# integration #

```
#!/bin/bash

# 0. prepare settings
INTEGRA_BASE_URL="http://127.0.0.1:8000"
INTEGRA_SCHEMA_PATH="schema.json"
INTEGRA_APP_NAME="contacts_replica1"

# 1. create login/pass API user
AUTH="api-reader:MyPass39dza2es"

# 2. download swagger `curl`
curl -u "${AUTH}" "${INTEGRA_BASE_URL}/api/v1/schema/?format=openapi" -o "${INTEGRA_SCHEMA_PATH}"

# 3. generate integration app
python manage.py schema_to_models "${INTEGRA_SCHEMA_PATH}" "${INTEGRA_APP_NAME}" --options '{"skip_models":["HistoricalComment","HistoricalContact","User"],"skip_fields":["_type"]}'

echo Add "${INTEGRA_APP_NAME}" to INSTALLED_APPS
echo
echo Setup integration settings like:
echo
echo "INTEGRA_CONFIGS = [                                        "
echo "    ...                                                    "
echo "    {                                                      "
echo "        'base_url': '${INTEGRA_BASE_URL}',                 "
echo "        'request': {                                       "
echo "            'auth': '${AUTH}',                             "
echo "        },                                                 "
echo "        'models': [                                        "
echo "            {'url': '/api/v1/<model>-list/',               "
echo "             'app': '${INTEGRA_APP_NAME}',                 "
echo "             'model': '<model>'},                          "
echo "            ...                                            "
echo "        ],                                                 "
echo "    }                                                      "
echo "    ...                                                    "
echo "]                                                          "
echo
echo Run: python manage.py makemigrations "${INTEGRA_APP_NAME}"
echo Run: python manage.py migrate
echo Setup: CELERY_BEAT_SCHEDULE in settings
```
