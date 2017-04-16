#!/usr/bin/env bash

set -e

exec gosu unprivileged "$@"
