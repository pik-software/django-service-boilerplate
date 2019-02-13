#!/usr/bin/env bash

[[ "${TRACE}" = "1" ]] && set -x
set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - init-dokku-back.sh $@"

SSH_HOST=$1
SERVICE_HOST=$2
SERVICE_NAME=$3
ENVIRONMENT=$4
MEDIA_ROOT=/DATA/${SERVICE_NAME}

if [[ -z "${SSH_HOST}" ]] || [[ -z "${SERVICE_HOST}" ]] || [[ -z "${SERVICE_NAME}" ]] || [[ -z "${ENVIRONMENT}" ]]; then
    echo "Use: $0 <SSH_HOST> <SERVICE_HOST> <SERVICE_NAME> <ENVIRONMENT>"
    exit 1
fi

if ssh dokku@${SSH_HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "App ${SERVICE_NAME} is already exists on ${SSH_HOST}";
    exit 2
fi

ssh ${SSH_HOST} -C sudo mkdir "${MEDIA_ROOT}"
ssh ${SSH_HOST} -C dokku events:on
ssh ${SSH_HOST} -C dokku apps:create ${SERVICE_NAME}
ssh dokku@${SSH_HOST} -C storage:mount ${SERVICE_NAME} "${MEDIA_ROOT}:${MEDIA_ROOT}"
ssh dokku@${SSH_HOST} -C domains:set ${SERVICE_NAME} ${SERVICE_HOST}

# postgres (root required!)
ssh ${SSH_HOST} -C POSTGRES_IMAGE="mdillon/postgis" POSTGRES_IMAGE_VERSION="9.6" dokku postgres:create ${SERVICE_NAME}
ssh dokku@${SSH_HOST} -C postgres:link ${SERVICE_NAME} ${SERVICE_NAME}

# redis
ssh dokku@${SSH_HOST} -C redis:create ${SERVICE_NAME}
ssh dokku@${SSH_HOST} -C redis:link ${SERVICE_NAME} ${SERVICE_NAME}

# dd-agent
if ssh ${SSH_HOST} -C docker ps | grep -q dd-agent; then
    # link to dd-agent
    ssh dokku@${SSH_HOST} -C docker-options:add ${SERVICE_NAME} build,deploy,run "--link dd-agent:dd-agent"
fi

# CONFIGS

SECRET_KEY=$( openssl rand -base64 18 )

# base
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} SERVICE_NAME=${SERVICE_NAME}
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_APP_TYPE=dockerfile
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} SECRET_KEY=${SECRET_KEY} > /dev/null
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} ENVIRONMENT=${ENVIRONMENT}
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} MEDIA_ROOT=${MEDIA_ROOT}

# lets encrypt
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_LETSENCRYPT_EMAIL=pik-software-team@pik-comfort.ru

# gcloud file storage
#ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND=
#ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BUCKET_NAME=
#ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_PROJECT_ID=
#ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} FILE_STORAGE_BACKEND_CREDENTIALS=

# sentry
#ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} RAVEN_DSN=

# OPTIONS
ssh dokku@${SSH_HOST} -C ps:set-restart-policy ${SERVICE_NAME} always
ssh dokku@${SSH_HOST} -C docker-options:add ${SERVICE_NAME} deploy,run "--memory=1Gb"
ssh dokku@${SSH_HOST} -C docker-options:add ${SERVICE_NAME} build "--memory=2Gb"

# SCALE
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DEFAULT_CHECKS_WAIT=0
ssh dokku@${SSH_HOST} -C ps:scale ${SERVICE_NAME} web=1 worker=1 beat=1
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DEFAULT_CHECKS_WAIT=5
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_WAIT_TO_RETIRE=60
ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} DOKKU_DOCKER_STOP_TIMEOUT=600
