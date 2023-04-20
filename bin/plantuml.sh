#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
    msg="${1}"
    echo "Error: ${msg}"
    echo "$(basename "$0") <file>"
    exit 1
}
file="${1-""}"
test -f "${file}" || usage "File does not exist"
docker run -i plantuml/plantuml:latest -pipe -tpng < "${file}" > "${file%.*}.png"
