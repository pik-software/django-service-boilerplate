#!/bin/bash

if [ "$ENVIRONMENT" = "staging" ]
then
  concurrency=1
else
  concurrency=${2:-$CELERY_WORKER_CONCURRENCY}
fi
queue_name=${1:-celery}
exec python -u -m celery worker -A _project_ --loglevel info -Q $queue_name -c $concurrency
