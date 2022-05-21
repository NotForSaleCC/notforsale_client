#!/bin/ash

set -e

if ( [ -z "${USERNAME}" ] || [ -z "${PASSWORD}" ] || ${BROKER} ); then
  echo "USERNAME, PASSWORD of BROKER are not defined"
  exit 1
fi

exec "$@"