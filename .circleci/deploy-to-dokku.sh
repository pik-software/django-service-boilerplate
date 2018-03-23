#!/usr/bin/env bash
set -x

REPO=`git config --local remote.origin.url|sed -n 's#.*/\([^.]*\)\.git#\1#p'`
BRANCH=`git branch | grep -e "^*" | cut -d' ' -f 2`

echo "DEPLOY !!! http://${REPO}-${BRANCH}.pik-software.ru/"
git push ssh://dokku@staging.pik-software.ru/${REPO}-${BRANCH} ${BRANCH}:master || exit 1
ssh dokku@staging.pik-software.ru -C "run ${REPO}-${BRANCH} python manage.py migrate" || exit 2
echo "OPEN FRESH !!! http://${REPO}-${BRANCH}.pik-software.ru/"
