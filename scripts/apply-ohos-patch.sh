#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${ROOT}/zig-bootstrap"
BASE="b12ab1fbafc3a290d6a13c42b14e1c67dd826c0f"
PATCH="${ROOT}/patch/zig-ohos-0.17.x.patch"

if ! git -C "${BOOTSTRAP}" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "${ROOT}" submodule update --init zig-bootstrap
fi
[[ -f "${PATCH}" ]] || { printf 'patch not found: %s\n' "${PATCH}" >&2; exit 1; }

actual="$(git -C "${BOOTSTRAP}" rev-parse HEAD)"
if [[ "${actual}" != "${BASE}" ]]; then
  printf 'zig-bootstrap base mismatch\nexpected: %s\nactual:   %s\n' \
    "${BASE}" "${actual}" >&2
  exit 1
fi

if git -C "${BOOTSTRAP}" apply --whitespace=nowarn --reverse --check "${PATCH}" >/dev/null 2>&1; then
  printf 'OHOS patch is already applied\n'
  exit 0
fi

git -C "${BOOTSTRAP}" apply --whitespace=nowarn --check "${PATCH}"
git -C "${BOOTSTRAP}" apply --whitespace=nowarn "${PATCH}"
printf 'applied OHOS patch to zig-bootstrap %s\n' "${BASE}"
