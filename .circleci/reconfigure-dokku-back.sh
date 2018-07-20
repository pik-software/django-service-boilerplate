#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - reconfigure-dokku-back.sh $@"

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
if [[ -z "$BRANCH" ]]; then
    echo "Use: $0 $HOST $SERVICE_NAME <BRANCH>"
    exit 1
fi

# CONFIGS
case "$DEPLOYMENT_PLACE" in
    production)
        ./set-configs-to-prod.sh ${HOST} ${SERVICE_NAME} ${BRANCH}
        ;;
    staging)
        ./set-configs-to-staging.sh ${HOST} ${SERVICE_NAME} ${BRANCH}
        ;;
esac
