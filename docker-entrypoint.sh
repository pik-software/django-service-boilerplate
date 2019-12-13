#!/usr/bin/env bash

set -e

chown unprivileged:unprivileged ${MEDIA_ROOT}
exec gosu unprivileged "$@"
