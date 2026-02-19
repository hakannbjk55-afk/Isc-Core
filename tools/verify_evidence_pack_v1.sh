#!/usr/bin/env bash
set -euo pipefail

PACK_TAR="${1:-}"
PACK_SHA="${2:-}"

if [ -z "$PACK_TAR" ] || [ -z "$PACK_SHA" ]; then
  echo "usage: verify_evidence_pack_v1.sh <evidence_pack_v1.tar> <evidence_pack_v1.sha256>"
  exit 2
fi

if [ ! -f "$PACK_TAR" ]; then
  echo "[VERIFY] ERROR: pack tar not found: $PACK_TAR"
  exit 3
fi

if [ ! -f "$PACK_SHA" ]; then
  echo "[VERIFY] ERROR: sha file not found: $PACK_SHA"
  exit 4
fi

echo "[VERIFY] Checking SHA256 of evidence pack..."
sha256sum -c "$PACK_SHA"

TMPDIR="$(mktemp -d)"
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

echo "[VERIFY] Extracting pack..."
tar -xf "$PACK_TAR" -C "$TMPDIR"

if [ ! -f "$TMPDIR/artifacts/ci_report.json" ]; then
  echo "[VERIFY] ERROR: missing artifacts/ci_report.json in pack"
  exit 5
fi

echo "[VERIFY] Computing deterministic CI report hash..."
REPORT_HASH="$(python3 tools/ci_report_hash_v1.py "$TMPDIR/artifacts/ci_report.json")"
echo "[VERIFY] CI_REPORT_HASH_V1: $REPORT_HASH"

echo "[VERIFY] PASS"
