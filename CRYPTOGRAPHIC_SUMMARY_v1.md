# ISC Core v1.0.0 — Cryptographic Summary
Tag: v1.0.0-isc-core-frozen

## Formal Security Statement

ISC Core v1 provides deterministic, cryptographically verifiable integrity of a recorded repository state and its associated CI output, bound to a specific signing key, with offline-verifiable proof packaging.

---

## 1. Executive Summary (Non-Technical)

ISC Core v1 is a cryptographic integrity framework.

It produces a signed, tamper-evident evidence bundle that proves:

- A specific repository state existed.
- That state produced a deterministic CI report.
- The report was signed by a specific cryptographic key.
- The evidence package has not been modified.
- Verification can be performed offline.

ISC Core v1 does not rely on blockchain, external logs, or third-party infrastructure.

It provides integrity guarantees, not correctness guarantees.

---

## 2. Technical Summary (Engineering View)

### Core Properties

ISC Core v1 enforces:

- Deterministic CI report hashing (CI_REPORT_V1)
- SHA256 reproducibility of evidence packages
- Namespace-bound Ed25519 signatures
- Principal-bound signature verification
- Attestation hash cross-verification
- Offline verifiability

### What It Proves

Given an evidence bundle, it cryptographically proves:

1. The CI report hash matches the recorded repository state.
2. The attestation hash binds the CI output deterministically.
3. The signature was created by the holder of a specific Ed25519 key.
4. The bundle contents have not changed since packaging.

### Trust Assumptions

Security depends on:

- Secure custody of the signing key
- Integrity of the CI environment at signing time
- Continued collision resistance of SHA256
- Continued security of Ed25519

### Threats Mitigated

- Post-build artifact tampering
- CI report modification after signing
- Namespace replay misuse
- Silent mutation of distributed evidence bundles

### Threats Not Mitigated

- Compromised signing key
- Malicious maintainer
- Compromised CI runner before signing
- Backdoored source code
- Legal identity binding of key owner

---

## 3. Legal / Assurance Boundaries

ISC Core v1 provides:

Cryptographic integrity assurance.

It does not provide:

- Legal notarization
- Identity verification of the signer
- Code correctness guarantees
- Security certification
- External timestamp authority anchoring

The system proves integrity and signer-binding of a state.
It does not prove the legitimacy or correctness of that state.

---

## 4. Classification

Security Level: Integrity Foundation
Assurance Model: Deterministic + Signed State Evidence
Release Status: Frozen (v1.0.0-isc-core-frozen)
