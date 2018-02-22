#!/usr/bin/env bash
set -x

REPO=$1
BRANCH=$2

echo "DEPLOY !!! http://${REPO}-${BRANCH}.pik-software.ru/"
git push ssh://dokku@staging.pik-software.ru/${REPO}-${BRANCH} ${BRANCH}:master || exit 1
ssh dokku@staging.pik-software.ru -C "run ${REPO}-${BRANCH} python manage.py migrate" || exit 2
ssh dokku@staging.pik-software.ru -C "run ${REPO}-${BRANCH} python _bin/generate_staging_data.py" || exit 3
echo "OPEN FRESH !!! http://${REPO}-${BRANCH}.pik-software.ru/"
