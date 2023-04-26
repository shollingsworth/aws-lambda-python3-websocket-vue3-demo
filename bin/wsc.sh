#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

env="${1:-""}"

case "${env}" in
    "local")
        url="ws://localhost:3001/ws?token=${TOKEN}"
        ;;
    "dev")
        url="wss://xbbv6yjs83.execute-api.us-east-2.amazonaws.com/dev?token=${TOKEN}"
        ;;
    *)
        echo " Didn't match anything"
        exit 1
        ;;
esac

wscat --connect "${url}"
