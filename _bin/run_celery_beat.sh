#!/bin/bash

CELERY_BEAT_PID_PATH=/tmp/celerybeat.pid
rm $CELERY_BEAT_PID_PATH
exec python -u -m celery beat -A _project_ --loglevel info --pidfile=$CELERY_BEAT_PID_PATH --schedule="/tmp/celerybeat-schedule.db"
