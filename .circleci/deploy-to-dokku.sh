#!/usr/bin/env bash

REPO=$1
BRANCH=$2

git push ssh://dokku@staging.pik-software.ru/${REPO}-${BRANCH} ${BRANCH}:master
