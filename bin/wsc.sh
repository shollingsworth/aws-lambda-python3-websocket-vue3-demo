#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

stage="${1:-""}"
if [[ "${stage}" != "prod" && "${stage}" != "dev" && "${stage}" != "local" ]]; then
    echo "Usage: $0 <stage>"
    exit 1
fi

ws= "$(
    aws cloudformation describe-stacks --stack-name "${prefix}-backend-${stage}"
        --query "Stacks[0].Outputs[?OutputKey=='${output_key}'].OutputValue" \
        --output text
)"

case "${stage}" in
    "local")
        url="ws://localhost:3001/ws?token=${TOKEN}"
        ;;
    "dev")
    "prod")
        url="${ws}?token=${TOKEN}"
        ;;
    *)
        echo " Didn't match anything"
        exit 1
        ;;
esac

wscat --connect "${url}"
