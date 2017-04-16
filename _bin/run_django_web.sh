#!/bin/bash

nprocessors=$(($(nproc) * 2))

#python manage.py migrate
exec uwsgi --module _project_.wsgi --processes $nprocessors --http :8000 --master --die-on-term --enable-threads --single-interpreter --wsgi-disable-file-wrapper --limit-post 4294967296
