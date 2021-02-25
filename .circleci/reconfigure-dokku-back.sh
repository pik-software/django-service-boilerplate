#!/usr/bin/env bash

[[ "${TRACE}" = "1" ]] && set -x
set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - reconfigure-dokku-back.sh $@"

SSH_HOST=$1
SERVICE_HOST=$2
SERVICE_NAME=$3
BRANCH=$4
ENVIRONMENT=$5

if [[ -z "${SSH_HOST}" ]] || [[ -z "${SERVICE_HOST}" ]] || [[ -z "${SERVICE_NAME}" ]] || [[ -z "${BRANCH}" ]] || [[ -z "${ENVIRONMENT}" ]]; then
    echo "Use: $0 <SSH_HOST> <SERVICE_HOST> <SERVICE_NAME> <BRANCH> <ENVIRONMENT>"
    exit 1
fi

RELEASE_DATE=$( date '+%Y-%m-%d-%H-%M-%S' )
RELEASE=$(git describe --tags --match v[0-9]*)
GIT_REV=$(git rev-parse ${BRANCH})

ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} \
RELEASE_DATE="'"${RELEASE_DATE}"'" \
RELEASE=${RELEASE} \
SENTRY_RELEASE=${RELEASE} \
GIT_REV=${GIT_REV}

# CONFIGS
case "$ENVIRONMENT" in
    production)
        ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} EXAMPLE=1
        ;;
    staging)
        ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} EXAMPLE=2
        ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} BRANCH=${BRANCH}
        ;;
esac

if [[ -n "${SENTRY_URL}" && -n "${SENTRY_TEAM}" && -n "${SENTRY_API_KEY}" ]]; then
    echo "Run SENTRY DSN discovery"
    SENTRY_DSN=$(python3 get-sentry-dsn.py -a "${SENTRY_URL}" -p "${SERVICE_NAME}" -t "${SENTRY_TEAM}" -k "${SENTRY_API_KEY}")
    ssh dokku@${SSH_HOST} -C config:set --no-restart ${SERVICE_NAME} SENTRY_DSN=${SENTRY_DSN}
else
    echo "No SENTRY DSN discovery settings (skip)"
fi
