#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - init-dokku-back.sh $@"

HOST=$1
SERVICE_NAME=$2
BRANCH=$3
DEPLOYMENT_PLACE=$4

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

ssh root@${HOST} -C dokku apps:create $SERVICE_NAME

# postgres (root required!)
ssh root@${HOST} -C POSTGRES_IMAGE="mdillon/postgis" POSTGRES_IMAGE_VERSION="9.6" dokku postgres:create $SERVICE_NAME
ssh dokku@${HOST} -C postgres:link $SERVICE_NAME $SERVICE_NAME

# redis
ssh dokku@${HOST} -C redis:create $SERVICE_NAME
ssh dokku@${HOST} -C redis:link $SERVICE_NAME $SERVICE_NAME

# CONFIGS
case "$DEPLOYMENT_PLACE" in
    production)
        ./set-configs-to-prod.sh ${HOST} ${SERVICE_NAME} ${BRANCH}
        ;;
    staging)
        ./set-configs-to-staging.sh ${HOST} ${SERVICE_NAME} ${BRANCH}
        ;;
esac

ssh dokku@${HOST} -C ps:set-restart-policy $SERVICE_NAME always

if ssh root@${HOST} -C docker ps | grep -q dd-agent; then
    # link to dd-agent
    ssh dokku@${HOST} -C docker-options:add $SERVICE_NAME build,deploy,run "--link dd-agent:dd-agent"
fi
