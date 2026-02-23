#!/usr/bin/env bash
set -euo pipefail

# 1) Core CI policy çalıştır (artifacts üretir)
./tools/ci_policy.sh

CI_REPORT="artifacts/ci_report.json"
PACK_MANIFEST="artifacts/evidence_pack_manifest_v1.sha256"

if [ ! -f "$CI_REPORT" ]; then
  echo "missing $CI_REPORT" >&2
  exit 1
fi

if [ ! -f "$PACK_MANIFEST" ]; then
  echo "missing $PACK_MANIFEST" >&2
  exit 1
fi

# 2) HASH'leri çek
STATE_HASH="$(python tools/ci_report_hash_v1.py "$CI_REPORT" | grep -Eo '[0-9a-f]{64}' | head -n1)"
PACK_HASH="$(grep -Eo '[0-9a-fA-F]{64}' "$PACK_MANIFEST" | head -n1 | tr 'A-F' 'a-f')"

if [ -z "$STATE_HASH" ] || [ -z "$PACK_HASH" ]; then
  echo "failed to extract hashes" >&2
  exit 1
fi

# 3) Stateless attestation üret (prev otomatik 000..)
python modules/time_layer_v1/tools/attest_release.py "$STATE_HASH" "$PACK_HASH"

# 4) Verify (tek dosya)
python modules/time_layer_v1/tools/verify_attestation.py modules/time_layer_v1/out/attestation.json

# 5) Timestamp'li kopya üret (artifact için)
TS="$(date -u +"%Y%m%dT%H%M%SZ")"
mkdir -p modules/time_layer_v1/out/attestations
cp modules/time_layer_v1/out/attestation.json \
   modules/time_layer_v1/out/attestations/attestation_${TS}.json

echo "OK: wrote modules/time_layer_v1/out/attestations/attestation_${TS}.json"
echo "STATE_HASH=$STATE_HASH"
echo "PACK_HASH=$PACK_HASH"
