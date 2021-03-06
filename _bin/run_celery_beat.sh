#!/bin/bash

exec python -u \
-m celery beat \
-A _project_ \
--loglevel info \
--pidfile=/tmp/celerybeat.pid \
--scheduler="redbeat.RedBeatScheduler"
