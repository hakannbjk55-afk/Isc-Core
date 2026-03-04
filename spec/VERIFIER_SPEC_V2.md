# ISC Evidence Pack V2 — Verifier Specification

## Overview

The ISC verifier validates an Evidence Pack by checking:

- pack identity
- content integrity
- governance authority
- timestamp anchoring
- pipeline lineage

Verification MUST be deterministic and reproducible.
The verifier MUST produce identical results when executed by different implementations using the same evidence pack.

## Verification Inputs

- evidence_pack.tar
- optional parent packs
- optional timestamp anchor provider

Verification SHOULD be possible offline except for timestamp anchor lookup.

## Step 1 — Extract Evidence Pack

Expected files:
ci_report.json
content_manifest.sha256
/governance/*
/time_layer/*
/artifacts/*
If any required file is missing: `verification = FAIL`

## Step 2 — Validate Content Integrity
for each file in content_manifest:
computed_hash = sha256(file)
if computed_hash != manifest_hash:
verification = FAIL
content_hash = SHA256(content_manifest)
## Step 3 — Validate Metadata

Canonicalize ci_report.json then compute:
meta_hash = SHA256(meta_json)
Extract required fields:
pack_hash, meta_hash, content_hash
event_type, parents, inputs, outputs
## Step 4 — Recompute Pack Identity
pack_hash_expected = SHA256(meta_hash || content_hash)
if pack_hash_expected != pack_hash:
verification = FAIL
## Step 5 — Verify Timestamp Anchor

The verifier MUST confirm:
pack_hash exists in anchor layer
If no anchor is found: `verification = FAIL`

## Step 6 — Governance Verification

Required checks:

**Allowed Signer**
signing key MUST appear in allowed_signers
**Revocation Check**
key MUST NOT appear in revocation_records
**Key Rotation**
key rotation history MUST be respected
If any rule fails: `verification = FAIL`

## Step 7 — Signature Verification
ed25519_verify(signature, content_hash, signer_public_key)
If signature validation fails: `verification = FAIL`

## Step 8 — Lineage Verification
for parent in parents:
verify parent pack
parent.outputs ⊆ child.inputs
If lineage rule fails: `verification = FAIL`

## Final Verification Result

If all steps succeed: `verification = SUCCESS`
PACK VERIFIED
Event:             release
Timestamp:         valid
Governance:        valid
Content integrity: valid
Lineage:           valid
The verifier MAY provide additional diagnostic information but MUST clearly indicate whether verification succeeded or failed.
