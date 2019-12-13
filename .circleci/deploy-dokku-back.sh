#!/usr/bin/env bash

[[ "${TRACE}" = "1" ]] && set -x
set -eo pipefail
cd "$(dirname "$0")"
echo "$(date +%Y-%m-%d-%H-%M-%S) - deploy-dokku-back.sh $@"

SSH_HOST=$1
DOMAIN=$2
REPO=$3
BRANCH=$4
ENVIRONMENT=$5

if [[ -z "${SSH_HOST}" ]] || [[ -z "${DOMAIN}" ]] || [[ -z "$REPO" ]] || [[ -z "$BRANCH" ]] || [[ -z "$ENVIRONMENT" ]]; then
    SSH_HOST=8.8.8.8
    DOMAIN=pik-software.ru
    REPO=$( git config --local remote.origin.url | sed -n 's#.*/\([^.]*\)\.git#\1#p' )
    BRANCH=$( git branch | grep -e "^*" | cut -d' ' -f 2 )
    ENVIRONMENT=production
    echo "Use: $0 <SSH_HOST> <DOMAIN> <REPO_NAME> <BRANCH_NAME> <ENVIRONMENT>"
    echo "Example: $0 ${SSH_HOST} ${DOMAIN} ${REPO} ${BRANCH} ${ENVIRONMENT}"
    exit 1
fi

function escape {
    echo "$1" | tr A-Z a-z | sed "s/[^a-z0-9]/-/g" | sed "s/^-+\|-+$//g"
}

SSH_HOST=$( echo ${SSH_HOST} )
DOMAIN=$( echo ${DOMAIN} )
REPO=$( escape ${REPO} )
BRANCH=$( escape ${BRANCH} )
ENVIRONMENT=$( escape ${ENVIRONMENT} )

echo "SSH_HOST=${SSH_HOST}"
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
    SERVICE_HOST="${REPO}.${DOMAIN}"
elif [[ "$ENVIRONMENT" = "staging" ]]; then
    SERVICE_NAME="${REPO}-${BRANCH}"
    SERVICE_HOST="${REPO}-${BRANCH}.${DOMAIN}"
else
    echo "!!! ERROR: UNKNOWN ENVIRONMENT !!!"
    exit 1
fi

echo "SERVICE_NAME=${SERVICE_NAME}"
echo "SERVICE_HOST=${SERVICE_HOST}"
echo "SSH: ${SSH_HOST}"

INIT_LETSENCRYPT=false
FIX_MEDIA_ROOT_PERMISSIONS=false

echo "Check SSH access 'ssh ${SSH_HOST} -o ConnectTimeout=10 dokku help'"
ssh ${SSH_HOST} -C dokku help > /dev/null
echo "Check SSH access 'ssh ${SSH_HOST} -o ConnectTimeout=10 docker ps'"
ssh ${SSH_HOST} -C docker ps > /dev/null
echo "Check SSH access 'ssh dokku@${SSH_HOST} -o ConnectTimeout=10 help'"
ssh dokku@${SSH_HOST} -C help > /dev/null

if ! ssh dokku@${SSH_HOST} -C apps:list | grep -qFx ${SERVICE_NAME}; then
    echo "!!! ===> Init <=== !!!"
    ./init-dokku-back.sh "${SSH_HOST}" "${SERVICE_HOST}" "${SERVICE_NAME}" "${ENVIRONMENT}"
    [[ -n "${LETSENCRYPT}" ]] && export INIT_LETSENCRYPT=true
fi

echo "!!! ===> Reconfigure <=== !!!"
./reconfigure-dokku-back.sh "${SSH_HOST}" "${SERVICE_HOST}" "${SERVICE_NAME}" "${BRANCH}" "${ENVIRONMENT}"

echo "!!! ===> Deploy <=== !!!"
git push ssh://dokku@${SSH_HOST}/${SERVICE_NAME} ${BRANCH}:master

if ${INIT_LETSENCRYPT}; then
    echo "!!! ===> Init letsencrypt certs <=== !!!"
    ssh dokku@${SSH_HOST} -C letsencrypt ${SERVICE_NAME}
fi

echo "!!! ===> Run migrations <=== !!!"
ssh dokku@${SSH_HOST} -C run ${SERVICE_NAME} python manage.py migrate

echo "!!! ===> http://${SERVICE_HOST}/ <=== !!!"
