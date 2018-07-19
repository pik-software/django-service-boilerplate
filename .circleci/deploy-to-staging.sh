#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - deploy-to-staging.sh $@"

HOST=$1
REPO=$2
BRANCH=$3

if [[ -z "$HOST" ]]; then
    echo "Use: $0 <HOST>"
    exit 1
fi

if [[ -z "$REPO" ]]; then
    REPO=$( git config --local remote.origin.url | sed -n 's#.*/\([^.]*\)\.git#\1#p' )
fi
if [[ -z "$BRANCH" ]]; then
    BRANCH=$( git branch | grep -e "^*" | cut -d' ' -f 2 )
fi

function escape {
    echo "$1" | tr A-Z a-z | sed "s/[^a-z0-9]/-/g" | sed "s/^-+\|-+$//g"
}

REPO=$( escape ${REPO} )
BRANCH=$( escape ${BRANCH} )
SERVICE_NAME="${REPO}-${BRANCH}"
INIT_LETSENCRYPT=false

if ! ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "Init ${SERVICE_NAME} on ${HOST}"
    ./init-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH} staging
    INIT_LETSENCRYPT=true
fi

./reconfigure-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH} staging

git push ssh://dokku@${HOST}/${SERVICE_NAME} ${BRANCH}:master

if ${INIT_LETSENCRYPT}; then
    ssh dokku@${HOST} -C letsencrypt $SERVICE_NAME
fi

# run migrations
ssh dokku@${HOST} -C run $SERVICE_NAME python manage.py migrate

echo "open !!! http://${SERVICE_NAME}.pik-software.ru/"
