#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-artifacts}"
mkdir -p "$OUT_DIR"

# TIME (UTC)
UTC_NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ENV fingerprint (deterministic, stable-ish fields)
OS_NAME="$(uname -s 2>/dev/null || true)"
OS_REL="$(uname -r 2>/dev/null || true)"
ARCH="$(uname -m 2>/dev/null || true)"

# GitHub Actions provides runner info; keep empty if not present
RUNNER_OS="${RUNNER_OS:-}"
RUNNER_ARCH="${RUNNER_ARCH:-}"
GITHUB_SHA="${GITHUB_SHA:-}"
GITHUB_REF="${GITHUB_REF:-}"
GITHUB_RUN_ID="${GITHUB_RUN_ID:-}"
GITHUB_RUN_ATTEMPT="${GITHUB_RUN_ATTEMPT:-}"

# Tool versions (best effort)
PY_VER="$(python3 --version 2>/dev/null || python --version 2>/dev/null || true)"
GIT_VER="$(git --version 2>/dev/null || true)"
TAR_VER="$(tar --version 2>/dev/null | head -n 1 || true)"
SHA_VER="$(sha256sum --version 2>/dev/null | head -n 1 || true)"

cat > "$OUT_DIR/envtime.json" <<JSON
{
  "time_utc": "${UTC_NOW}",
  "env": {
    "uname_s": "${OS_NAME}",
    "uname_r": "${OS_REL}",
    "uname_m": "${ARCH}",
    "runner_os": "${RUNNER_OS}",
    "runner_arch": "${RUNNER_ARCH}",
    "python": "${PY_VER}",
    "git": "${GIT_VER}",
    "tar": "${TAR_VER}",
    "sha256sum": "${SHA_VER}"
  },
  "github": {
    "sha": "${GITHUB_SHA}",
    "ref": "${GITHUB_REF}",
    "run_id": "${GITHUB_RUN_ID}",
    "run_attempt": "${GITHUB_RUN_ATTEMPT}"
  }
}
JSON

# fingerprint hash
sha256sum "$OUT_DIR/envtime.json" | awk '{print $1}' > "$OUT_DIR/envtime.sha256"

echo "[envtime] wrote: $OUT_DIR/envtime.json"
echo "[envtime] sha256: $(cat "$OUT_DIR/envtime.sha256")"
