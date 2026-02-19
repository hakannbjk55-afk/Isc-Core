#!/bin/bash
# verify_evidence_pack_v1.sh
# Usage: bash verify_evidence_pack_v1.sh evidence_pack_v1.tar evidence_pack_v1.sha256
set -euo pipefail

TAR="${1:-}"
SHA="${2:-}"

if [[ -z "$TAR" || -z "$SHA" ]]; then
  echo "[VERIFY] FAIL: usage: verify_evidence_pack_v1.sh <pack.tar> <pack.sha256>"
  exit 1
fi

echo "[VERIFY] Checking pack integrity..."
sha256sum -c "$SHA" || { echo "[VERIFY] FAIL: pack hash mismatch"; exit 1; }

echo "[VERIFY] Extracting manifest..."
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
tar -xf "$TAR" -C "$TMPDIR"

MANIFEST="$TMPDIR/artifacts/evidence_pack_manifest_v1.sha256"
if [[ ! -f "$MANIFEST" ]]; then
  echo "[VERIFY] FAIL: manifest not found inside pack"
  exit 1
fi

echo "[VERIFY] Checking internal manifest..."
cd "$TMPDIR"
sha256sum -c "$MANIFEST" || { echo "[VERIFY] FAIL: internal manifest mismatch"; exit 1; }

echo "[VERIFY] PASS: pack integrity and manifest verified"
