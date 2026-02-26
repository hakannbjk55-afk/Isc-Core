# SECURITY MODEL — ISC Core v13.0.0-audit

## 1. Trust Boundary

ISC defines a strict integrity boundary between:

- Governance state (signed registry)
- CI artifact generation
- Evidence pack production
- Offline verification consumer

No untrusted input may mutate governance state.
All state transitions require valid cryptographic authorization.

---

## 2. Evidence Pack Structure

An evidence pack (v2) contains:

- Artifact binaries
- SHA256 manifest
- CI report (deterministic JSON)
- Governance signature
- Key rotation metadata (if applicable)

All hashes are computed using deterministic ordering rules.

---

## 3. Verification Flow

1. Verify governance key signature
2. Verify key is not revoked
3. Verify artifact SHA256 matches manifest
4. Verify CI report hash matches deterministic CI_REPORT_V1
5. Verify manifest integrity
6. Produce final verdict

If any step fails → VERDICT: REJECT

---

## 4. Failure Conditions

Verification MUST fail under:

- Hash mismatch
- Signature invalid
- Key revoked
- Missing artifact binding
- CI report tampering
- Manifest mutation

System fails closed.

---

## 5. Offline Verification Guarantees

Verification requires:

- No network
- No external trust anchor
- No timestamp server

All required trust material is embedded in the evidence pack.

Deterministic reproducibility is guaranteed given identical input artifacts.

