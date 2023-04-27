#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

trap "exit" INT TERM ERR
trap "kill 0" EXIT

aws logs describe-log-groups \
    --log-group-name-prefix "/aws/lambda/sh-ws-demo-backend-dev" \
    --query 'logGroups[].logGroupName' \
    | jq -r '.[]' | while read logGroupName; do
        echo "Tailing $logGroupName"
        aws logs tail \
            "$logGroupName" \
            --since 10m \
            --follow &
    done

while true; do
    sleep 1
done
