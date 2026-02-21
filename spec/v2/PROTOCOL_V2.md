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

