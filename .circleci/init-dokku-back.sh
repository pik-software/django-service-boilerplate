#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - init-dokku-back.sh $@"

HOST=$1
SERVICE_NAME=$2

if [[ -z "$HOST" ]]; then
    echo "Use: $0 <HOST>"
    exit 1
fi
if [[ -z "$SERVICE_NAME" ]]; then
    echo "Use: $0 $HOST <SERVICE_NAME>"
    exit 1
fi

if ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "App ${SERVICE_NAME} is already exists on ${HOST}";
    exit 2
fi

SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

ssh root@${HOST} -C apps:create $SERVICE_NAME

# postgres (root required!)
ssh root@${HOST} -C POSTGRES_IMAGE="mdillon/postgis" POSTGRES_IMAGE_VERSION="9.6" dokku postgres:create $SERVICE_NAME
ssh dokku@${HOST} -C postgres:link $SERVICE_NAME $SERVICE_NAME

# redis
ssh dokku@${HOST} -C redis:create $SERVICE_NAME
ssh dokku@${HOST} -C redis:link $SERVICE_NAME $SERVICE_NAME

# CONFIGS

# base
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME SERVICE_NAME=$SERVICE_NAME
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME DOKKU_APP_TYPE=dockerfile
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME SECRET_KEY=$SECRET_KEY

# environment
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME ENVIRONMENT=staging

# lets encrypt
ssh dokku@${HOST} -C config:set --no-restart $SERVICE_NAME DOKKU_LETSENCRYPT_EMAIL=it-services@pik-comfort.ru

ssh dokku@${HOST} -C ps:set-restart-policy $SERVICE_NAME always
ssh dokku@${HOST} -C ps:scale $SERVICE_NAME worker=1 beat=1
