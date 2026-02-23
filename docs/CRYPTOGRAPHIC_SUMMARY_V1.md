# ISC Core — Cryptographic Summary V1

## 1. Purpose

This document defines what ISC Core cryptographically guarantees and what it does not.
It is a normative summary of the system’s trust boundaries.

ISC Core is designed as a deterministic, tamper-evident, governance-enforced evidence engine.

## 2. What ISC Core Guarantees

### 2.1 Deterministic State Integrity

Given the same repository state and canonicalization rules:

- The CI report is deterministic.
- The CI report hash (CI_REPORT_V1) is stable.
- The Evidence Pack V2 archive is reproducible.
- Hashes are content-derived, not environment-derived.

This guarantees:

If two parties build from the same state, they obtain identical hashes.

### 2.2 Tamper-Evident Evidence

Evidence Pack V2 includes:

- CI report
- Signed attestation
- Governance rotation record
- Governance revocation record
- Hash manifests

The verifier enforces:

- Archive SHA256 integrity
- Signature validity
- Rotation signature validity
- Revocation signature validity
- Rotation enforcement logic

This guarantees:

Any modification of the package or governance records is detectable.

### 2.3 Signed Attestation

Release attestations are signed using Ed25519.

The verifier confirms:

- Signature validity
- Namespace binding
- Key identity match

This guarantees:

The attestation was produced by the declared signing key.

### 2.4 Governance Enforcement

Rotation and revocation records are:

- Hash-derived
- Cryptographically signed
- Included in the evidence bundle
- Verified during offline validation

The verifier enforces:

- Revoked keys cannot be used after effective_timestamp
- Rotation records must match signature

This guarantees:

Key lifecycle events are cryptographically bound and enforceable.

### 2.5 Offline Verifiability

All required verification artifacts are included inside Evidence Pack V2.
No external service is required.

This guarantees:

Verification can be performed without network access.

## 3. What ISC Core Does NOT Guarantee

ISC Core does NOT guarantee:

- Absolute time truth (only declared timestamps)
- External notarization
- Hardware root of trust
- Multi-party quorum (current policy: 1-of-1)
- Protection against compromised private keys prior to revocation
- Protection against malicious code intentionally committed before freeze

ISC Core provides cryptographic integrity and governance enforcement, not behavioral correctness of code.

## 4. Trust Model

Current governance policy:

- Quorum: 1-of-1
- Key rotation supported
- Revocation enforced
- Core protocol frozen

Future expansion may introduce:

- Multi-signer quorum
- External anchoring
- Governance hash chaining

## 5. System Classification

ISC Core is:

- Deterministic
- Tamper-evident
- Cryptographically signed
- Governance-aware
- Offline verifiable

ISC Core is not:

- A blockchain
- A public timestamp authority
- A consensus network
- A distributed trust system (yet)

## 6. Conclusion

ISC Core provides a portable, enforceable, cryptographically verifiable evidence system.

Its strength lies in:

- Deterministic builds
- Signed state attestations
- Enforced governance lifecycle
- Strict core freeze discipline

This document defines the trust boundary of ISC Core V1.
