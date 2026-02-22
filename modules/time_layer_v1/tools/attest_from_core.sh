#!/usr/bin/env bash
set -euo pipefail

# Inputs (core artifacts)
CI_REPORT_JSON="artifacts/ci_report.json"
PACK_MANIFEST="artifacts/evidence_pack_manifest_v1.sha256"
PACK_FILE="artifacts/evidence_pack_v1.tar"

# Outputs (time layer)
OUT_DIR="modules/time_layer_v1/out"
ARCHIVE_DIR="$OUT_DIR/attestations"

# 1) sanity
test -f "$CI_REPORT_JSON" || { echo "ERR: missing $CI_REPORT_JSON (run ./tools/ci_policy.sh first)"; exit 2; }
test -f "$PACK_MANIFEST"  || { echo "ERR: missing $PACK_MANIFEST (run ./tools/ci_policy.sh first)"; exit 2; }

mkdir -p "$OUT_DIR" "$ARCHIVE_DIR"

# 2) compute state_hash from ci_report.json using core tool
STATE_HASH="$(python tools/ci_report_hash_v1.py "$CI_REPORT_JSON" | tr -d ' \n\r\t')"

# 3) read pack sha256 from manifest (first token)
PACK_HASH="$(sha256sum "$PACK_FILE" | awk '{print $1}' | tr -d ' \n\r\t' )"

# 4) determine prev_attestation_hash = last attestation_hash if exists else GENESIS via script default
PREV=""
LAST_FILE="$(ls -1 "$ARCHIVE_DIR"/*.json 2>/dev/null | sort | tail -n 1 || true)"
if [ -n "${LAST_FILE}" ]; then
  PREV="$(jq -r .attestation_hash "$LAST_FILE")"
fi

# 5) produce attestation.json
if [ -n "${PREV}" ]; then
  modules/time_layer_v1/tools/attest_release.py "$STATE_HASH" "$PACK_HASH" "$PREV"
else
  modules/time_layer_v1/tools/attest_release.py "$STATE_HASH" "$PACK_HASH"
fi

# 6) archive with timestamp (monotonic by name)
TS="$(date -u +"%Y%m%dT%H%M%SZ")"
NAME="attestation_${TS}.json"
cp "$OUT_DIR/attestation.json" "$ARCHIVE_DIR/$NAME"

# 7) verify full chain
modules/time_layer_v1/tools/verify_chain.py

echo "OK: wrote $ARCHIVE_DIR/$NAME"
echo "STATE_HASH=$STATE_HASH"
echo "PACK_HASH=$PACK_HASH"
