#!/bin/bash

NPROCESSORS="${NPROCESSORS:-$(($(nproc) * 2))}"
PORT="${PORT:-5000}"
UWSGI_EXTRA_ARGS="${UWSGI_EXTRA_ARGS:-}"
#UWSGI_EXTRA_ARGS="--wsgi-disable-file-wrapper"

#python manage.py migrate
exec uwsgi --static-map /static=$STATIC_ROOT --static-map /media=$MEDIA_ROOT --module _project_.wsgi --processes $NPROCESSORS --http :$PORT --master --die-on-term --enable-threads --single-interpreter --limit-post 4294967296 $UWSGI_EXTRA_ARGS
