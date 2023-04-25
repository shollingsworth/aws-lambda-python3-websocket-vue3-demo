#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
FE="${DIR}/../frontend"
DIST="${FE}/dist"


stage="${1}"

cfid() {
    ws="${1}"
    aws --region us-east-2 \
        cloudfront list-distributions \
        --query "DistributionList.Items[?Aliases.Items!=null] |
        [?contains(Aliases.Items, '${ws}')].Id | [0]" \
        --output text | tee
}

invalidate() {
    cfid="${1}"
    aws --region us-east-2 \
        cloudfront create-invalidation \
        --distribution-id "${cfid}" \
        --paths "/*" \
        --output text | tee
}

syncs3() {
    bucket="${1}"
    aws --region us-east-2 \
        s3 sync "${DIST}" "s3://${bucket}" \
        --delete \
        --output text | tee
}


case "${stage}" in
    "prod")
        ws="sh-ws-demo.stev0.me"
        bucket="sh-ws-demo-prod-s3cf"
        export VITE_STAGE="prod"
        rm -rfv "${DIST}/*"
        cd "${FE}"
        npm run build
        id="$(cfid "${ws}")"
        syncs3 "${bucket}"
        invalidate "${id}"
        ;;
    "dev")
        ws="sh-ws-demo-dev.stev0.me"
        bucket="sh-ws-demo-dev-s3cf"
        export VITE_STAGE="dev"
        rm -rfv "${DIST}/*"
        id="$(cfid "${ws}")"
        cd "${FE}"
        npm run build
        syncs3 "${bucket}"
        invalidate "${id}"
        ;;
    *)
        echo "invalid stage ${stage}"
        echo "Usage: $0 [dev|prod]"
        exit 1
esac
