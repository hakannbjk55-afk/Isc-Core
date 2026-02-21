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

