#!/usr/bin/env bash

REPO=$1

echo "git push ssh://dokku@staging.pik-software.ru/${REPO}-master master"
