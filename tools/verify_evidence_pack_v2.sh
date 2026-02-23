#!/usr/bin/env bash
set -euo pipefail

TAR="${1:-artifacts/evidence_pack_v2.tar}"
MAN="${2:-artifacts/evidence_pack_manifest_v2.sha256}"

[ -f "$TAR" ] || { echo "missing $TAR" >&2; exit 1; }
[ -f "$MAN" ] || { echo "missing $MAN" >&2; exit 1; }

echo "[V2] checking tar sha256 vs manifest..."
EXP="$(awk '{print $1}' "$MAN" | head -n1)"
GOT="$(sha256sum "$TAR" | awk '{print $1}')"
[ "$EXP" = "$GOT" ] || { echo "sha256 mismatch" >&2; exit 1; }
echo "[V2] sha256 OK"

TMP="$(mktemp -d)"
tar -xf "$TAR" -C "$TMP"

ATT="$TMP/artifacts/time_layer_v1_signed/attestation.json"
PROOF="$TMP/artifacts/time_layer_v1_signed/attestation_proof.json"
ALLOW="$TMP/artifacts/time_layer_v1_signed/keys/allowed_signers"
SIG="$TMP/artifacts/time_layer_v1_signed/attestation_hash.txt.sig"
HASH_TXT="$TMP/artifacts/time_layer_v1_signed/attestation_hash.txt"

[ -f "$ATT" ] || { echo "missing attestation.json in tar" >&2; exit 1; }
[ -f "$PROOF" ] || { echo "missing attestation_proof.json in tar" >&2; exit 1; }
[ -f "$ALLOW" ] || { echo "missing allowed_signers in tar" >&2; exit 1; }
[ -f "$SIG" ] || { echo "missing signature file in tar" >&2; exit 1; }
[ -f "$HASH_TXT" ] || { echo "missing attestation_hash.txt in tar" >&2; exit 1; }

echo "[V2] verifying signature..."
NS_EXPECT="isc-core.time_layer_v1.attestation"
SIG_ID="$(jq -r '.signer_id' "$PROOF" | tr -d '\r\n')"

ssh-keygen -Y verify -f "$ALLOW" -I "$SIG_ID" -n "$NS_EXPECT" -s "$SIG" < "$HASH_TXT" >/dev/null

echo "[V2] signature OK"

ATT_HASH="$(jq -r '.attestation_hash' "$ATT" | tr -d '\r\n')"
PROOF_HASH="$(jq -r '.attestation_hash' "$PROOF" | tr -d '\r\n')"
[ "$ATT_HASH" = "$PROOF_HASH" ] || { echo "attestation_hash mismatch" >&2; exit 1; }

echo "OK: evidence_pack_v2 verified"
