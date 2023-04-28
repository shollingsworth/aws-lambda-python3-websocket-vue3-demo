#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG="${DIR}/../config.json"
FE="${DIR}/../frontend"
DIST="${FE}/dist"

stage="${1}"
if [[ -z "${stage}" ]]; then
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

if [[ ! -f "${CONFIG}" ]]; then
    echo "config file not found: ${CONFIG}"
    exit 1
fi

if [[ ! -d "${FE}" ]]; then
    echo "frontend directory not found: ${FE}"
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
bucket="${prefix}-${stage}-s3cf"
stack_name="${prefix}-backend-${stage}"
output_key="ServiceEndpointWebsocket"


export AWS_REGION="${region}"


cfid() {
    ws="${1}"
    aws \
        cloudfront list-distributions \
        --query "DistributionList.Items[?Aliases.Items!=null] |
        [?contains(Aliases.Items, '${ws}')].Id | [0]" \
        --output text | tee
}

invalidate() {
    cfid="${1}"
    aws \
        cloudfront create-invalidation \
        --distribution-id "${cfid}" \
        --paths "/*" \
        --output text | tee
}

syncs3() {
    bucket="${1}"
    aws \
        s3 sync "${DIST}" "s3://${bucket}" \
        --delete \
        --output text | tee
}

build() {
    rm -rfv "${DIST}/*"
    cd "${FE}"
    npm run build
}

echo "Deploying frontend to ${stage}..."
source <(${DIR}/frontend_env.sh "${stage}")
for key in VITE_STAGE VITE_AWS_REGION VITE_USER_POOL_ID VITE_CLIENT_ID VITE_FQDN VITE_WEBSOCKET VITE_COGNITO_DOMAIN; do
    echo "${key}=${!key}"
done


build
id="$(cfid "${VITE_FQDN}")"
syncs3 "${bucket}"
invalidate "${id}"
