#!/usr/bin/env bash
set -euo pipefail

ATTEST_JSON="${1:-}"
KEY="${2:-}"
OUTDIR="${3:-}"

if [[ -z "$ATTEST_JSON" || -z "$KEY" || -z "$OUTDIR" ]]; then
  echo "usage: sign_attestation.sh <attestation_json> <private_key> <out_dir>" >&2
  exit 2
fi

mkdir -p "$OUTDIR"

NS="isc-core.time_layer_v1.attestation"
SIGNER_ID="time_layer_v1"
NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

ATT_HASH="$(jq -r '.attestation_hash' "$ATTEST_JSON" | tr -d '\r\n')"

if [[ ! "$ATT_HASH" =~ ^[0-9a-f]{64}$ ]]; then
  echo "bad attestation_hash: $ATT_HASH" >&2
  exit 1
fi

PAYLOAD="$OUTDIR/attestation_hash.txt"
printf "%s\n" "$ATT_HASH" > "$PAYLOAD"

ssh-keygen -Y sign -f "$KEY" -I "$SIGNER_ID" -n "$NS" "$PAYLOAD" >/dev/null

SIG="$PAYLOAD.sig"
KEY_ID="$(ssh-keygen -lf "${KEY}.pub" -E sha256 | awk '{print $2}')"
SIG_SHA256="$(sha256sum "$SIG" | awk '{print $1}')"

cat > "$OUTDIR/attestation_proof.json" <<JSON
{"version":"TIME_LAYER_V1_PROOF","type":"ssh-ed25519","namespace":"$NS","signer_id":"$SIGNER_ID","key_id":"$KEY_ID","signed_at_utc":"$NOW","attestation_hash":"$ATT_HASH","sig_file":"$(basename "$SIG")","sig_sha256":"$SIG_SHA256"}
JSON

echo "OK: signed attestation_hash"
