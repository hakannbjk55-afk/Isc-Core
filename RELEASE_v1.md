# ISC Core v1.0.0 — Frozen

## Status
Frozen foundation release.

## Guarantees

- Deterministic CI report hashing (CI_REPORT_V1)
- Tamper-evident enforcement gates
- Signed attestation (Ed25519, SSH-based)
- Offline signature verification
- Evidence Pack V2 (self-contained, reproducible)
- Public key + allowed_signers inclusion inside bundle

## Security Properties

- Hash determinism enforced
- Signature namespace enforced
- Principal binding enforced
- Attestation hash cross-check enforced
- Reproducible tar packaging

## Scope

This release defines the foundational trust model.

Not included:
- Key rotation policy
- Sigstore anchoring
- External transparency logs
- Mandatory CI signature enforcement

These will build on top of this frozen base.

---

Tag: v1.0.0-isc-core-frozen
