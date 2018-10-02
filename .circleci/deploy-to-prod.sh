#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - deploy-to-prod.sh $@"

REPO=$( git config --local remote.origin.url | sed -n 's#.*/\([^.]*\)\.git#\1#p' )
HOST=$REPO.pik-software.ru
BRANCH=master
CURRENT_BRANCH=$( git branch | grep -e "^*" | cut -d' ' -f 2 )
HAS_RELEASE_TAG=$( git tag --points-at HEAD | grep -q "^v" && echo 1 || echo 0 )

if [[ "$CURRENT_BRANCH" != "master" ]]; then
    echo "Deploy only master!"
    exit 1
fi
if [[ "$HAS_RELEASE_TAG" != "1" ]]; then
    echo "Release tag required!"
    exit 2
fi

SERVICE_NAME="${REPO}"
INIT_LETSENCRYPT=false

if ! ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "Init ${SERVICE_NAME} on ${HOST}"
    ./init-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH} production
    ./reconfigure-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH} production
    INIT_LETSENCRYPT=true
fi

git push ssh://dokku@${HOST}/${SERVICE_NAME} ${BRANCH}:master

if ${INIT_LETSENCRYPT}; then
    ssh dokku@${HOST} -C letsencrypt $SERVICE_NAME
fi

echo "open !!! http://${SERVICE_NAME}.pik-software.ru/"
