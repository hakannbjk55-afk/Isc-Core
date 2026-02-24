# ISC Core — Cryptographic Summary V1

## 1. Purpose

This document defines the cryptographic guarantees of ISC Core V1.

It describes:

- What is cryptographically enforced
- What is content-derived vs environment-derived
- What integrity boundaries exist
- What is explicitly NOT guaranteed

This document defines the trust boundary of ISC Core.

---

## 2. Deterministic State Integrity

ISC Core enforces deterministic CI outputs.

Given the same repository state and canonicalization rules:

- `ci_report.json` is deterministic
- `CI_REPORT_V1` hash is stable
- Evidence Pack V2 archive is reproducible
- Hashes are content-derived (not environment-derived)

Guarantee:

Two independent builders using the same state produce identical hashes.

---

## 3. Evidence Pack Integrity

Evidence Pack V2 includes:

- CI report
- Signed attestation
- Governance rotation record
- Governance revocation record
- Artifact binding manifest
- SHA256 manifest

Verification enforces:

- Archive SHA256 integrity
- Manifest consistency
- Signature validity
- Governance signature validity
- Artifact digest format validation

Guarantee:

Any modification to the bundle is detectable.

---

## 4. Signed Attestation Model

Attestations are signed using Ed25519.

Verifier enforces:

- Signature validity
- Namespace binding
- Key identity match

Guarantee:

The attestation was produced by the declared signing key.

Limitation:

If the private key is compromised before revocation,
forged attestations may appear valid.

---

## 5. Governance Lifecycle Enforcement

Governance records are:

- Content-derived
- Hash-bound
- Cryptographically signed
- Included inside the evidence bundle

Verifier enforces:

- Rotation signature validity
- Revocation signature validity
- Revoked keys cannot sign after effective_timestamp

Guarantee:

Key lifecycle events are cryptographically enforceable.

Limitation:

Current governance policy is 1-of-1 (single signer).

---

## 6. Artifact Binding

Artifact manifests bind produced artifacts to evidence.

Each subject includes:

- SHA256 digest
- Algorithm identifier
- Name
- Source

Verifier enforces:

- Digest format correctness
- Manifest hash integrity

Guarantee:

Artifacts referenced in the bundle are cryptographically identified.

Limitation:

If deployment systems do not enforce digest matching,
final-mile swap remains possible.

---

## 7. Offline Verifiability

All verification artifacts are included in Evidence Pack V2.

No external service is required.

Guarantee:

Verification can be performed without network access.

Limitation:

Time claims are declared, not externally notarized.

---

## 8. What ISC Core Does NOT Guarantee

ISC Core does NOT provide:

- Consensus truth
- External timestamp authority
- Hardware root-of-trust
- Multi-party quorum governance (V1)
- Behavioral correctness guarantees
- Protection against key theft prior to revocation

ISC Core provides cryptographic integrity,
not distributed trust.

---

## 9. Cryptographic Primitives

- SHA256 (content hashing)
- Ed25519 (signatures)
- Deterministic JSON canonicalization (project-defined)

All guarantees depend on the correctness of these primitives.

---

## 10. Trust Boundary Definition

ISC Core V1 defines a portable, enforceable,
cryptographically verifiable evidence boundary.

Strength comes from:

- Deterministic hashing
- Signed state commitments
- Enforced governance lifecycle
- Strict protocol freeze discipline

This document defines the cryptographic scope of ISC Core V1.

