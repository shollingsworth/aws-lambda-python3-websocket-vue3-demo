#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

trap "exit" INT TERM ERR
trap "kill 0" EXIT
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "${DIR}/../backend"
source .in
npm run offline &

cd "${DIR}/../frontend"
npm run dev &



while true; do
    sleep 1
done
