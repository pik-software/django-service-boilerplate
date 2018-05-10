#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - deploy-to-prod.sh $@"

HOST=35.234.72.31
REPO=$( git config --local remote.origin.url | sed -n 's#.*/\([^.]*\)\.git#\1#p' )
BRANCH=master
CURRENT_BRANCH=$( git branch | grep -e "^*" | cut -d' ' -f 2 )

if [[ "$BRANCH" != "$CURRENT_BRANCH" ]]; then
    echo "Deploy only master!"
    exit 1
fi

SERVICE_NAME="${REPO}"
INIT_LETSENCRYPT=false

if ! ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "Init ${SERVICE_NAME} on ${HOST}"
    ./init-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH}
    INIT_LETSENCRYPT=true
fi

./reconfigure-dokku-back.sh ${HOST} ${SERVICE_NAME} ${BRANCH}

git push ssh://dokku@${HOST}/${SERVICE_NAME} ${BRANCH}:master

if ${INIT_LETSENCRYPT}; then
    ssh dokku@${HOST} -C letsencrypt $SERVICE_NAME
fi

echo "open !!! http://${SERVICE_NAME}.pik-software.ru/"
