#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - reconfigure-dokku-back.sh $@"

HOST=$1
SERVICE_NAME=$2
BRANCH=$3

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

case "$BRANCH" in
    example1)
        RELEASE_DATE=$( date '+%Y-%m-%d-%H-%M-%S' )
        ;;
    *)
        RELEASE_DATE=$( date )
        ;;
esac

ssh dokku@${HOST} -C config:set --no-restart ${SERVICE_NAME} RELEASE_DATE="'"${RELEASE_DATE}"'"
