#!/bin/bash

# defaults
case "$ENVIRONMENT" in
 staging) default_concurrency=1 ;;
 *) default_concurrency=2 ;;
esac
default_queue_name=celery

# args -> env -> default
queue_name=${1:-${CELERY_WORKER_QUEUE_NAME:-$default_queue_name}}
concurrency=${2:-${CELERY_WORKER_CONCURRENCY:-$default_concurrency}}

export CELERY_WORKER_QUEUE_NAME="${queue_name}"
export CELERY_WORKER_CONCURRENCY="${concurrency}"
exec python -u -m celery worker -A _project_ --loglevel info -Q $queue_name -c $concurrency
