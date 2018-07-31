#!/usr/bin/env bash

set -ex

HOST=$1
SERVICE_NAME=$2
BRANCH=$3

RELEASE_DATE=$( date '+%Y-%m-%d-%H-%M-%S' )
SECRET_KEY=$( openssl rand -base64 18 )

# base
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME SERVICE_NAME=$SERVICE_NAME
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME DOKKU_APP_TYPE=dockerfile
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME SECRET_KEY=$SECRET_KEY
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME DOKKU_DOCKER_STOP_TIMEOUT=600

# lets encrypt
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME DOKKU_LETSENCRYPT_EMAIL=pik-software-team@pik-comfort.ru

ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} RELEASE_DATE="'"${RELEASE_DATE}"'"
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} ENVIRONMENT=production

# gcloud file storage
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BUCKET_NAME=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_PROJECT_ID=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND_CREDENTIALS=

# sentry
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} RAVEN_DSN=
