#!/usr/bin/env sh
set -eu

echo "[CI] Policy: vectors gate with tolerance on missing verifier"

if [ -f tools/vector_verifier.py ]; then
  echo "[CI] Found tools/vector_verifier.py -> running (GATE)"
  python3 --version || true
  python3 tools/vector_verifier.py
  echo "[CI] Vector verifier OK"
else
  echo "[CI] WARNING: tools/vector_verifier.py not found -> tolerated (RECOVERY)"
  echo "[CI][TELEMETRY] missing_vector_verifier=1"
fi
