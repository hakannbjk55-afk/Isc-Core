# ISC Key Registry v1 (Draft)

Status: DRAFT
Layer: Protocol v2

## Purpose

Defines the authoritative public keys allowed to sign ISC evidence packs.

## Registry Properties

- Append-only
- Deterministic ordering
- Immutable historical entries
- No in-place mutation

## Registry Format (normative)

Registry MUST be a JSON array of objects:

[
  {
    "key_id": "<string>",
    "algorithm": "ed25519",
    "public_key_hex": "<hex>",
    "status": "active"
  }
]

## Rules

- key_id MUST be unique
- algorithm currently MUST be "ed25519"
- public_key_hex MUST be lowercase hex
- status MUST be one of: active | revoked

Revocation MUST NOT delete entries.
Revocation MUST change status to "revoked".


## Registry Snapshot Anchoring (normative)

A seal MUST reference a specific registry snapshot.

The registry snapshot identifier MUST be:

`SHA256(registry_file_bytes)`

Seal metadata (`seal.json`) MUST include:

"registry_sha256": "<hex>"

Verification procedure MUST:

1) Compute SHA256 of the registry file used.
2) Compare with seal.json registry_sha256.
3) Verify signature using a key that:
   - exists in that registry snapshot
   - has status "active"

A seal MUST NOT validate unless the referenced registry snapshot contains the signing key with status "active".

Historical seals remain valid if:
- The key was active in the referenced registry snapshot.


## Canonical Binding (normative)

The Key Registry snapshot identity MUST be derived from Core canonicalization.

Implementations MUST:

1) Parse the registry JSON as strict JSON.
2) Canonicalize it using Canonical Core v1 (major=12).
3) Compute:

   registry_id =
   SHA256( ISC_REGISTRY_V1\0 || SHA256(canonical_registry_bytes) )

Where:
- canonical_registry_bytes are the exact UTF-8 bytes produced by Core canonicalization.
- SHA256(...) is the raw 32-byte digest.
- ISC_REGISTRY_V1\0 is an ASCII domain-separation prefix.

### Informational hash (non-normative)

Implementations MAY compute:

   file_sha256 = SHA256(registry_file_bytes)

However, file_sha256 MUST NOT be used as the authoritative registry identifier.

