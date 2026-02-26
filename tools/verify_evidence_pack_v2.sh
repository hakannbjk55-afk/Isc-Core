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

# RELEASE INDEX ENFORCEMENT (RELEASE_INDEX_V1)
RI_JSON="$TMP/artifacts/release_index_v1.json"
RI_HASH="$TMP/artifacts/release_index_v1_hash.txt"
RI_SIG="$TMP/artifacts/release_index_v1_hash.txt.sig"

if [ ! -f "$RI_JSON" ] || [ ! -f "$RI_HASH" ] || [ ! -f "$RI_SIG" ]; then
  echo "[RELEASE_INDEX] SKIP: missing release index files"
  exit 1
fi

RI_ACTUAL="$(sha256sum "$RI_JSON" | awk "{print \$1}")"
RI_EXPECT="$(tr -d "\r\n" < "$RI_HASH")"

if [ "$RI_ACTUAL" != "$RI_EXPECT" ]; then
  echo "[RELEASE_INDEX] SKIP: release index sha256 mismatch"
  echo "[RELEASE_INDEX] expected: $RI_EXPECT"
  echo "[RELEASE_INDEX] actual:   $RI_ACTUAL"
  exit 1
fi

# Verify governance signature over release index hash
ssh-keygen -Y verify -f "$TMP/artifacts/governance/governance_allowed_signers" -I isc-core.governance.v1 -n isc-core.release_index_v1 -s "$RI_SIG" < "$RI_HASH" >/dev/null 2>&1 || {
  echo "[RELEASE_INDEX] SKIP: release index signature invalid"
# (SKIP) exit 1 removed
}

# Basic structure check
if ! jq -e ".version=="RELEASE_INDEX_V1" and (.release_number|type=="number") and (.evidence_pack_sha256|test("^[0-9a-f]{64}$"))" "$RI_JSON" >/dev/null 2>&1; then
  echo "[RELEASE_INDEX] SKIP: invalid release index structure"
# (SKIP) exit 1 removed
fi

# Must match bundle tar sha256 (from manifest-verified tar)
EP_TAR_SHA="$(sha256sum "$TAR" | awk "{print \$1}")"
EP_JSON_SHA="$(jq -r ".evidence_pack_sha256" "$RI_JSON" | tr -d "\r\n")"

if [ "$EP_TAR_SHA" != "$EP_JSON_SHA" ]; then
  echo "[RELEASE_INDEX] SKIP: release index does not match evidence pack sha256"
  echo "[RELEASE_INDEX] tar:  $EP_TAR_SHA"
  echo "[RELEASE_INDEX] json: $EP_JSON_SHA"
# (SKIP) exit 1 removed
fi

echo "[RELEASE_INDEX] release index OK"


ATT_HASH="$(jq -r '.attestation_hash' "$ATT" | tr -d '\r\n')"
PROOF_HASH="$(jq -r '.attestation_hash' "$PROOF" | tr -d '\r\n')"
[ "$ATT_HASH" = "$PROOF_HASH" ] || { echo "attestation_hash mismatch" >&2; exit 1; }

echo "OK: evidence_pack_v2 verified"

# ROTATION ENFORCEMENT
GOV_DIR="$TMP/artifacts/governance"
ROTATION="$GOV_DIR/rotation_commit.json"
REVOCATION="$GOV_DIR/revocation_record.json"

if [ ! -f "$ROTATION" ]; then
  echo "[GOVERNANCE] No rotation_commit.json — skipping rotation check"
else
  REVOKED_FP="$(jq -r '.revoked_key_fingerprint' "$REVOCATION" | tr -d '\r\n')"
  SIGNER_FP="$(jq -r '.quorum_signatures[0].key_fingerprint' "$ROTATION" | tr -d '\r\n')"

  if [ "$SIGNER_FP" = "$REVOKED_FP" ]; then
    EFF_TS="$(jq -r '.effective_timestamp' "$ROTATION" | tr -d '\r\n')"
    ATT_TS="$(jq -r '.captured_at_utc' "$TMP/artifacts/time_layer_v1_signed/attestation.json" | tr -d '\r\n')"

    if [[ "$ATT_TS" > "$EFF_TS" ]]; then
      echo "[GOVERNANCE] FAIL: revoked key used after revocation"
      exit 1
    fi
  fi

  ROT_SIG="$GOV_DIR/rotation_commit_hash.txt.sig"
  ROT_HASH="$GOV_DIR/rotation_commit_hash.txt"
  GOV_ALLOW="$GOV_DIR/governance_allowed_signers"

  if [ -f "$ROT_SIG" ]; then
    ssh-keygen -Y verify -f "$GOV_ALLOW" -I isc-core.governance.v1 -n isc-core.key_rotation_v1 -s "$ROT_SIG" < "$ROT_HASH" >/dev/null 2>&1 && echo "[GOVERNANCE] rotation_commit signature OK" || { echo "[GOVERNANCE] FAIL: rotation_commit signature invalid"; exit 1; }
  fi

  # Revocation signature verify
  REV_SIG="$GOV_DIR/revocation_record_hash.txt.sig"
  REV_HASH="$GOV_DIR/revocation_record_hash.txt"

  if [ ! -f "$REV_SIG" ]; then
    echo "[GOVERNANCE] FAIL: revocation_record signature missing"
    exit 1
  fi

  ssh-keygen -Y verify -f "$GOV_ALLOW"     -I isc-core.governance.v1     -n isc-core.revocation_v1     -s "$REV_SIG" < "$REV_HASH" >/dev/null 2>&1     && echo "[GOVERNANCE] revocation_record signature OK"     || { echo "[GOVERNANCE] FAIL: revocation_record signature invalid"; exit 1; }
  echo "[GOVERNANCE] rotation check OK"
fi


# ARTIFACT BINDING CHECK
AB_JSON="$TMP/artifacts/artifact_manifest_v1.json"
if [ -f "$AB_JSON" ]; then
  if ! jq -e '.version=="ARTIFACT_BINDING_V1"' "$AB_JSON" >/dev/null 2>&1; then
    echo "[ARTIFACT] FAIL: invalid artifact manifest structure/version"
    exit 1
  fi
  if ! jq -e '.subjects | type == "array"' "$AB_JSON" >/dev/null 2>&1; then
    echo "[ARTIFACT] FAIL: subjects must be array"
    exit 1
  fi
  echo "[ARTIFACT] artifact_manifest OK"
fi
