#!/usr/bin/env bash

set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - reconfigure.sh $@"

HOST=$1
SERVICE_NAME=$2
BRANCH=$3
ENVIRONMENT=$4

if [[ -z "${HOST}" ]] || [[ -z "${SERVICE_NAME}" ]] || [[ -z "${BRANCH}" ]] || [[ -z "${ENVIRONMENT}" ]]; then
    echo "Use: $0 <HOST> <SERVICE_NAME> <BRANCH> <ENVIRONMENT>"
    exit 1
fi

RELEASE_DATE=$( date '+%Y-%m-%d-%H-%M-%S' )
ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} RELEASE_DATE="'"${RELEASE_DATE}"'"

# CONFIGS
case "$ENVIRONMENT" in
    production)
        ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} EXAMPLE=1
        ;;
    staging)
        ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} EXAMPLE=2
        ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} BRANCH=${BRANCH}
        ;;
esac
