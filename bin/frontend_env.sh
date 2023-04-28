#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG="${DIR}/../config.json"

stage="${1-""}"
if [[ -z "${stage}" ]]; then
    echo "Usage: $(basename $0) [dev|prod]"
    exit 1
fi

if [[ ! -f "${CONFIG}" ]]; then
    echo "config file not found: ${CONFIG}"
    exit 1
fi

if [[ "${stage}" != "dev" && "${stage}" != "prod" ]]; then
    echo "invalid stage: ${stage}"
    exit 1
fi

getconfigkey() {
    key="${1}"
    jq -r ".${key}" "${CONFIG}"
}

prefix="$(getconfigkey "prefix")"
region="$(getconfigkey "region")"
export AWS_REGION="${region}"

getssm() {
    env_key="${1}"
    param="${2}"
    out=$(aws \
        ssm get-parameter \
        --name "${param}" \
        --query "Parameter.Value" \
        --output text | tee
    )
    # echo "# ${env_key}: ${out}"
    echo "export ${env_key}=${out}"
}

echo "export VITE_STAGE=${stage}"
echo "export VITE_AWS_REGION=${region}"
echo "export VITE_WEBSOCKET=$(
""
    aws cloudformation describe-stacks --stack-name "${prefix}-backend-${stage}"
        --query "Stacks[0].Outputs[?OutputKey=='ServiceEndpointWebsocket'].OutputValue" \
        --output text
)"
getssm VITE_USER_POOL_ID "/${prefix}/cognito_user_pool_id"
getssm VITE_CLIENT_ID "/${prefix}/cognito_user_pool_client_id"
getssm VITE_FQDN "/${prefix}/${stage}/fe_domain"
getssm VITE_COGNITO_DOMAIN "/${prefix}/cognito_fqdn"
