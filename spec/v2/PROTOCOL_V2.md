# ISC Protocol Layer v2 (Draft)

Status: DRAFT
Depends on: Canonical Core v1 (FROZEN, major=12)

## Version Binding

Protocol v2 implementations MUST bind to a specific Core major version.

Initial binding:
Core major = 12

If Core major changes, Protocol compatibility MUST be re-evaluated.

## Scope

Protocol v2 defines:

- Seal model (pack-level signing)
- Key registry contract
- Verification bundle format
- Release artifact structure
- Conformance distribution model

This layer MUST NOT modify canonical byte behavior defined by Core v1.

Any canonical change requires Core v2+.

## Boundary

Core v1:
- Canonicalization
- Error codes
- Conformance vectors
- Deterministic behavior

Protocol v2:
- Signing
- Sealing
- Key governance
- Distribution & verification packaging


## Seal Model (v2): Detached Signature

Protocol v2 uses a **detached** signature model.

### Artifacts
- `artifacts/evidence_pack_v1.tar` (bytes MUST remain unchanged)
- `artifacts/evidence_pack_v1.tar.sha256` (sha256 of pack bytes)
- `artifacts/evidence_pack_v1.tar.sig` (detached signature over pack bytes)
- `artifacts/evidence_pack_v1.seal.json` (optional: structured metadata envelope)

### Signing input (normative)
The signature MUST be computed over the exact bytes of `evidence_pack_v1.tar`.

The signing input MUST be domain-separated:

`ISC_SEAL_V1\0 || SHA256(evidence_pack_v1.tar)`

### Verification (normative)
A verifier MUST:
1) compute SHA256 over `evidence_pack_v1.tar` and compare with `*.sha256`
2) verify `*.sig` over `ISC_SEAL_V1\0 || <pack_sha256_bytes>`

### Rationale (non-normative)
Detached signatures preserve deterministic pack bytes and avoid self-referential packaging.

## Seal Metadata Envelope (seal.json)

If present, `evidence_pack_v1.seal.json` MUST follow this structure:

{
  "seal_version": "1",
  "core_major": 12,
  "pack_sha256": "<hex>",
  "signature_algorithm": "ed25519",
  "public_key_id": "<key-id>",
  "created_at": "<RFC3339 timestamp>"
}

### Field requirements (normative)

- seal_version: string, MUST be "1"
- core_major: integer, MUST match bound Core major (12)
- pack_sha256: lowercase hex SHA256 of pack bytes
- signature_algorithm: currently "ed25519"
- public_key_id: stable key identifier (string)
- created_at: RFC3339 UTC timestamp

The signature file (`*.sig`) MUST correspond to pack_sha256 declared here.

