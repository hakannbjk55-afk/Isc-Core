#!/usr/bin/env bash
set -euo pipefail

ATTEST_JSON="${1:-}"
PROOF_JSON="${2:-}"
ALLOWED="${3:-}"

if [[ -z "$ATTEST_JSON" || -z "$PROOF_JSON" || -z "$ALLOWED" ]]; then
  echo "usage: verify_signed_attestation.sh <attestation_json> <proof_json> <allowed_signers>" >&2
  exit 2
fi

NS_EXPECT="isc-core.time_layer_v1.attestation"

ATT_HASH="$(jq -r '.attestation_hash' "$ATTEST_JSON" | tr -d '\r\n')"
PROOF_HASH="$(jq -r '.attestation_hash' "$PROOF_JSON" | tr -d '\r\n')"
NS="$(jq -r '.namespace' "$PROOF_JSON" | tr -d '\r\n')"
SIGNER_ID="$(jq -r '.signer_id' "$PROOF_JSON" | tr -d '\r\n')"
SIG_FILE="$(jq -r '.sig_file' "$PROOF_JSON" | tr -d '\r\n')"

if [[ "$NS" != "$NS_EXPECT" ]]; then
  echo "namespace mismatch" >&2
  exit 1
fi

if [[ "$ATT_HASH" != "$PROOF_HASH" ]]; then
  echo "attestation_hash mismatch" >&2
  exit 1
fi

TMP="$(mktemp -d)"
PAYLOAD="$TMP/attestation_hash.txt"
printf "%s\n" "$ATT_HASH" > "$PAYLOAD"

SIG_PATH="$(dirname "$PROOF_JSON")/$SIG_FILE"

ssh-keygen -Y verify -f "$ALLOWED" -I "$SIGNER_ID" -n "$NS_EXPECT" -s "$SIG_PATH" < "$PAYLOAD" >/dev/null

echo "OK: signature verified"
