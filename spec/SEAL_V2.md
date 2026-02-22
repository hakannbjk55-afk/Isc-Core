# Seal v2 (ISC_SEAL_V2)

This document defines Seal v2: a detached signature format that cryptographically binds an Evidence Pack to a specific Registry snapshot state.

## Status
Normative.

## Goals
- Bind the seal not only to the pack content, but also to a specific registry snapshot state.
- Enable offline verification (no external lookup required).
- Preserve backward compatibility with Seal v1 by using a new domain-separated prefix.

## Terms
- **Pack SHA-256**: The SHA-256 digest of the exact Evidence Pack bytes (e.g., the `.tar` bytes), represented as raw 32 bytes when used in signing input.
- **Registry ID**: A domain-separated identifier selecting the registry namespace (UTF-8 string).
- **Registry Snapshot**: A deterministic snapshot artifact included inside the Evidence Pack (see "Pack integration").
- **Registry Snapshot Commitment**: SHA-256 of the registry snapshot canonical bytes, used as raw 32 bytes in signing input.

## Pack integration (REQUIRED)
The Evidence Pack MUST include exactly one registry snapshot artifact at:

- `registry/registry_snapshot.json`

The file MUST be UTF-8 encoded and MUST be canonicalized using the Core canonicalization rules before computing the snapshot commitment.

The registry snapshot MUST NOT include any self-referential field that depends on its own hash/commitment.

## Snapshot commitment (REQUIRED)
Let `REG_CANON_BYTES` be the canonical bytes of `registry/registry_snapshot.json` computed via Core canonicalization.

Then:

- `REG_SNAPSHOT_SHA256_BYTES = SHA256(REG_CANON_BYTES)` (raw 32 bytes)

## Signing input (REQUIRED)
Seal v2 signing input is the concatenation of four fields with a fixed prefix:

`ISC_SEAL_V2\0 || PACK_SHA256_BYTES || REGISTRY_ID_FIELD || REG_SNAPSHOT_SHA256_BYTES`

### REGISTRY_ID_FIELD encoding (REQUIRED)
To avoid concatenation ambiguity, `REGISTRY_ID_FIELD` MUST be length-prefixed:

- `REGISTRY_ID_FIELD = U32BE(len(REGISTRY_ID_BYTES)) || REGISTRY_ID_BYTES`
- `REGISTRY_ID_BYTES` is the UTF-8 encoding of `registry_id`.

### PACK_SHA256_BYTES encoding (REQUIRED)
`PACK_SHA256_BYTES` MUST be the raw 32-byte SHA-256 digest (not hex).

## Signature algorithm
- Algorithm: Ed25519
- The signature is computed over the Signing input bytes exactly as specified.

## Detached seal file (RECOMMENDED structure)
A detached seal file (e.g., `artifacts/seal_v2.json`) SHOULD include:

- `seal_version`: `"ISC_SEAL_V2"`
- `algo`: `"ed25519"`
- `pack_sha256`: hex string (display only; verifier MUST recompute)
- `registry_id`: string
- `registry_snapshot_sha256`: hex string (display only; verifier MUST recompute from snapshot file)
- `public_key_id`: string (key reference)
- `signature`: base64 or hex (implementation-defined; MUST be specified by the implementation using this spec)

## Verification (STRICT)
A STRICT verifier MUST:
1. Recompute `PACK_SHA256_BYTES` from the Evidence Pack bytes.
2. Read `registry/registry_snapshot.json` from inside the pack and compute `REG_SNAPSHOT_SHA256_BYTES` from its canonical bytes.
3. Reconstruct Signing input exactly.
4. Verify the Ed25519 signature against the declared public key.

If any required artifact is missing, verification MUST fail in STRICT mode.

## Verification (RECOVERY)
A RECOVERY verifier MAY accept the seal while recording a verification report that explicitly states which required registry-binding checks could not be performed.

RECOVERY mode MUST NOT be used for court-grade acceptance; it exists only for tooling transition and diagnostics.

## Backward compatibility
Seal v1 remains valid with its own prefix and signing input. Seal v2 MUST NOT reuse Seal v1 prefix.

## Golden Example (Normative)

Given:

- evidence_pack_v1.tar SHA256:
  26dce79bd20a67f8d5770aec04b5c641e11db0b5bbb91f1eb017df356261bec4

- registry_id:
  "ISC_REGISTRY_MAIN" (17 bytes)

- registry_snapshot canonical SHA256:
  1123d6eaeed404c6069a44bf71edf00f9ef9c2cd00993926a32c23da57d9e95b

The signing message MUST be constructed as:

ISC_SEAL_V2\0 ||
SHA256(evidence_pack_v1.tar) ||
U32BE(len(registry_id)) ||
registry_id (UTF-8 bytes) ||
SHA256(registry_snapshot canonical bytes)

For the above values:

- Message length: 97 bytes
- Message SHA256:
  4908ace6cf3f36ed4cf5222d3556a7c46563b2875404ab70371d26f1eaafc8d8

This value is normative and MUST remain stable unless the SEAL_V2 message construction contract changes (MAJOR version bump required).

