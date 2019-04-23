#!/bin/bash

# defaults
case "$ENVIRONMENT" in
 staging) default_concurrency=1 ;;
 *) default_concurrency=2 ;;
esac
default_queue_name=celery

# args -> default
queue_name=${1:-$default_queue_name}
concurrency=${2:-$default_concurrency}

exec python -u -m celery worker -A _project_ --loglevel info -Q $queue_name -c $concurrency
