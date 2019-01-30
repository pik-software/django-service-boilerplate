#!/usr/bin/env bash

[[ "${TRACE}" = "1" ]] && set -x
set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - init-dokku-back.sh $@"

HOST=$1
SERVICE_NAME=$2
ENVIRONMENT=$3

if [[ -z "${HOST}" ]] || [[ -z "${SERVICE_NAME}" ]] || [[ -z "${ENVIRONMENT}" ]]; then
    echo "Use: $0 <HOST> <SERVICE_NAME> <ENVIRONMENT>"
    exit 1
fi

if ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "App ${SERVICE_NAME} is already exists on ${HOST}";
    exit 2
fi

ssh ${HOST} -C dokku apps:create ${SERVICE_NAME}
ssh dokku@${HOST} -C domains:set ${SERVICE_NAME} ${SERVICE_NAME}

# postgres (root required!)
ssh ${HOST} -C POSTGRES_IMAGE="mdillon/postgis" POSTGRES_IMAGE_VERSION="9.6" dokku postgres:create ${SERVICE_NAME}
ssh dokku@${HOST} -C postgres:link ${SERVICE_NAME} ${SERVICE_NAME}

# redis
ssh dokku@${HOST} -C redis:create ${SERVICE_NAME}
ssh dokku@${HOST} -C redis:link ${SERVICE_NAME} ${SERVICE_NAME}

# dd-agent
if ssh ${HOST} -C docker ps | grep -q dd-agent; then
    # link to dd-agent
    ssh dokku@${HOST} -C docker-options:add ${SERVICE_NAME} build,deploy,run "--link dd-agent:dd-agent"
fi

# CONFIGS

SECRET_KEY=$( openssl rand -base64 18 )

# base
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} SERVICE_NAME=${SERVICE_NAME}
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_APP_TYPE=dockerfile
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} SECRET_KEY=${SECRET_KEY} > /dev/null
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} ENVIRONMENT=${ENVIRONMENT}

# lets encrypt
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_LETSENCRYPT_EMAIL=pik-software-team@pik-comfort.ru

# gcloud file storage
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BUCKET_NAME=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_PROJECT_ID=
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND_CREDENTIALS=

# sentry
#ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} RAVEN_DSN=

# OPTIONS
ssh dokku@${HOST} -C ps:set-restart-policy ${SERVICE_NAME} always
ssh dokku@${HOST} -C docker-options:add ${SERVICE_NAME} deploy,run "--memory=1Gb"
ssh dokku@${HOST} -C docker-options:add ${SERVICE_NAME} build "--memory=2Gb"

# SCALE
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DEFAULT_CHECKS_WAIT=0
ssh dokku@${HOST} -C ps:scale ${SERVICE_NAME} web=1 worker=1 beat=1
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DEFAULT_CHECKS_WAIT=5
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_WAIT_TO_RETIRE=60
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DOCKER_STOP_TIMEOUT=600
