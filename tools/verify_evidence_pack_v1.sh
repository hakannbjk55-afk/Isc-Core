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

echo "[VERIFY] Checking SEAL_V2..."

SEAL_FILE="$(pwd)/artifacts/seal_v2.json"

if [ -f "$SEAL_FILE" ]; then
  PACK_SHA_EXPECTED=$(grep '"pack_sha256"' "$SEAL_FILE" | cut -d '"' -f4)
  PACK_SHA_ACTUAL=$(sha256sum artifacts/evidence_pack_v1.tar | awk '{print $1}')

  if [ "$PACK_SHA_EXPECTED" != "$PACK_SHA_ACTUAL" ]; then
    echo "[VERIFY][FAIL] Pack SHA256 mismatch"
    exit 80
  fi

  REG_SNAP_EXPECTED=$(grep '"registry_snapshot_sha256"' "$SEAL_FILE" | cut -d '"' -f4)
  REG_SNAP_ACTUAL=$(sha256sum registry/registry_snapshot.canon | awk '{print $1}')

  if [ "$REG_SNAP_EXPECTED" != "$REG_SNAP_ACTUAL" ]; then
    echo "[VERIFY][FAIL] Registry snapshot SHA256 mismatch"
    exit 81
  fi

  SIG_B64=$(grep '"signature_b64"' "$SEAL_FILE" | cut -d '"' -f4)
  echo "$SIG_B64" | base64 -d > /tmp/seal_sig.bin

  openssl pkeyutl -verify \
    -pubin \
    -inkey registry/ed25519_public.pem \
    -rawin \
    -in registry/seal_v2_message.bin \
    -sigfile /tmp/seal_sig.bin

  if [ $? -ne 0 ]; then
    echo "[VERIFY][FAIL] Signature verification failed"
    exit 82
  fi

  echo "[VERIFY] SEAL_V2 verified"
else
  echo "[VERIFY] No seal_v2.json found (skipping)"
fi

