#!/bin/ash

set -e

if ( [ -z "${USERNAME}" ] || [ -z "${PASSWORD}" ] || [ -z "${BROKER}" ] || [ -z "${WEB}" ] ); then
  echo "USERNAME, PASSWORD, BROKER or WEB are not defined"
  exit 1
fi

exec "$@"