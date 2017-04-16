#!/bin/bash

exec python -u -m celery worker -A _project_ --loglevel info
