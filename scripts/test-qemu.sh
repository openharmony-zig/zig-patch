#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${ROOT}/scripts/apply-ohos-patch.sh"
exec "${ROOT}/zig-bootstrap/scripts/ohos/test-qemu.sh" "$@"
