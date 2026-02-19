#!/usr/bin/env bash
set -euo pipefail

FORBIDDEN_PATHS=(
  "spec/core"
  "core"
)

# Phi-related forbidden tokens (strict)
PATTERN="\\bphi\\b|1\\.618|1\\.618033|61\\.8|38\\.2"

hit=0

for p in "${FORBIDDEN_PATHS[@]}"; do
  if [ -d "$p" ]; then
    if rg -n -i "$PATTERN" "$p" >/dev/null 2>&1; then
      echo "[PHI_TRIPWIRE] Forbidden phi reference found under $p"
      rg -n -i "$PATTERN" "$p" || true
      hit=1
    fi
  fi
done

if [ "$hit" -ne 0 ]; then
  exit 61
fi

echo "[PHI_TRIPWIRE] OK"
