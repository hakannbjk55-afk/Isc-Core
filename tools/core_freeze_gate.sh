#!/usr/bin/env bash
set -euo pipefail

changed=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || true)

if echo "$changed" | grep -q "^core/"; then
  echo "[FREEZE_GATE] FAIL: core/ modification detected"
  echo "[FREEZE_GATE] Core is frozen. Use a module instead."
  exit 1
fi

echo "[FREEZE_GATE] OK: core/ untouched"
