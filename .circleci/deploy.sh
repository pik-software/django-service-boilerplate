#!/usr/bin/env bash

set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - deploy.sh $@"

HOST=$1
REPO=$2
BRANCH=$3
ENVIRONMENT=$4

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
if [[ -z "$ENVIRONMENT" ]]; then
    ENVIRONMENT=production
fi

function escape {
    echo "$1" | tr A-Z a-z | sed "s/[^a-z0-9]/-/g" | sed "s/^-+\|-+$//g"
}

HOST=$( echo ${HOST} )
REPO=$( escape ${REPO} )
BRANCH=$( escape ${BRANCH} )
ENVIRONMENT=$( escape ${ENVIRONMENT} )

echo "HOST=${HOST}"
echo "REPO=${REPO}"
echo "BRANCH=${BRANCH}"
echo "ENVIRONMENT=${ENVIRONMENT}"

if [[ "$ENVIRONMENT" = "production" ]]; then
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
elif [[ "$ENVIRONMENT" = "staging" ]]; then
    SERVICE_NAME="${REPO}-${BRANCH}"
else
    echo "Unknown environment!"
    exit 1
fi

INIT_LETSENCRYPT=false

if ! ssh dokku@${HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "Init SERVICE_NAME=${SERVICE_NAME} BRANCH=${BRANCH} ENVIRONMENT=${ENVIRONMENT} on ${HOST}"
    ./init.sh ${HOST} ${SERVICE_NAME} ${ENVIRONMENT}
    INIT_LETSENCRYPT=true
fi

echo "Reconfigure SERVICE_NAME=${SERVICE_NAME} BRANCH=${BRANCH} ENVIRONMENT=${ENVIRONMENT} on ${HOST}"
./reconfigure.sh ${HOST} ${SERVICE_NAME} ${BRANCH} ${ENVIRONMENT}

git push ssh://dokku@${HOST}/${SERVICE_NAME} ${BRANCH}:master

if ${INIT_LETSENCRYPT}; then
    ssh dokku@${HOST} -C letsencrypt ${SERVICE_NAME}
fi

# run migrations
ssh dokku@${HOST} -C run ${SERVICE_NAME} python manage.py migrate

echo "open !!! http://${HOST}/"
