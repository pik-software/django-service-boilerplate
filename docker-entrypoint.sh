#!/usr/bin/env bash

set -e

if [[ -z "${MEDIA_ROOT}" ]]; then
  chown unprivileged:unprivileged ${MEDIA_ROOT}
fi

exec gosu unprivileged "$@"
