#!/usr/bin/env bash

set -e

if [[ ! -z "${MEDIA_ROOT}" ]]; then
  chown unprivileged:unprivileged ${MEDIA_ROOT}
fi

if [[ ! -z "${PRIVATE_STORAGE_ROOT}" ]]; then
  mkdir -p "${PRIVATE_STORAGE_ROOT}"
  chown unprivileged:unprivileged ${PRIVATE_STORAGE_ROOT}
fi

exec gosu unprivileged "$@"
