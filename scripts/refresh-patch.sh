#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR="${OHOS_TMPDIR:-${ROOT}/zig-bootstrap/out/tmp}"
mkdir -p "${TMPDIR}"
export TMPDIR
BOOTSTRAP="${ROOT}/zig-bootstrap"
BASE="8a7dffbf56cdbcea8a19f10dc48f4ad1ea376252"
PATHS_FILE="${BOOTSTRAP}/ohos/source-paths.txt"
OUTPUT="${ROOT}/patch/zig-ohos-0.17.x.patch"
TEMP_INDEX="$(mktemp "${TMPDIR:-/tmp}/zig-ohos-index.XXXXXX")"
trap 'rm -f "${TEMP_INDEX}"' EXIT

git -C "${BOOTSTRAP}" cat-file -e "${BASE}^{commit}"
[[ -f "${PATHS_FILE}" ]] || { printf 'missing %s\n' "${PATHS_FILE}" >&2; exit 1; }

real_index="$(git -C "${BOOTSTRAP}" rev-parse --git-path index)"
cp "${real_index}" "${TEMP_INDEX}"
paths=()
while IFS= read -r path; do
  case "${path}" in ''|'#'*) continue ;; esac
  paths+=("${path}")
done <"${PATHS_FILE}"

GIT_INDEX_FILE="${TEMP_INDEX}" git -C "${BOOTSTRAP}" add -A -- "${paths[@]}"
GIT_INDEX_FILE="${TEMP_INDEX}" git -C "${BOOTSTRAP}" diff \
  --cached --binary --full-index "${BASE}" -- "${paths[@]}" >"${OUTPUT}"
[[ -s "${OUTPUT}" ]] || { printf 'generated patch is empty\n' >&2; exit 1; }

if command -v sha256sum >/dev/null 2>&1; then
  digest="$(sha256sum "${OUTPUT}" | awk '{print $1}')"
else
  digest="$(env LC_ALL=C LC_CTYPE=C LANG=C shasum -a 256 "${OUTPUT}" | awk '{print $1}')"
fi
printf '%s  %s\n' "${digest}" "$(basename "${OUTPUT}")" >"${OUTPUT}.sha256"
printf 'refreshed %s\n' "${OUTPUT}"
