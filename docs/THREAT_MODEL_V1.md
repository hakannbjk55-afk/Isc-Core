# ISC Core — Threat Model V1

## 1. Purpose

This document defines the formal threat model of ISC Core V1.

It specifies:

- What ISC Core protects
- Against whom it provides protection
- Which attacks are mitigated by design
- Which risks remain (residual risks)
- What ISC Core explicitly does NOT guarantee (non-goals)

ISC Core is a deterministic, tamper-evident, governance-enforced evidence engine designed for offline verifiability.

---

## 2. System Overview

ISC Core produces:

- A deterministic CI report (`ci_report.json`)
- A deterministic CI hash (`CI_REPORT_V1`)
- A reproducible Evidence Pack (`evidence_pack_v2.tar`) with manifest(s)
- Signed attestations (Ed25519)
- Governance lifecycle records (rotation + revocation), signed and enforced
- Artifact binding manifests (linking evidence to produced artifacts)

ISC Core’s protocol surface under `core/` is frozen (“frozen genome” discipline).  
All evolutions are expected to occur in modular layers (tools/, modules/, docs/, policy files).

ISC Core does NOT provide consensus, distributed trust, or an external timestamp authority by default.

---

## 3. Protected Assets

A1. **Repository State Integrity**  
The integrity of source and specifications that define the system state.

A2. **Deterministic CI Outputs**  
Determinism of `ci_report.json` and stability of `CI_REPORT_V1`.

A3. **Evidence Pack Integrity**  
Integrity and reproducibility of `evidence_pack_v2.tar` and its manifests.

A4. **Governance Records**  
Integrity of `rotation_commit.json`, `revocation_record.json`, and their signed hashes.

A5. **Signed Attestations**  
Authenticity of signed attestation objects and their namespace bindings.

A6. **Artifact Binding**  
Cryptographic linkage between evidence bundle and produced artifacts (digests).

A7. **Signing Keys**  
Confidentiality and correct operational use of private keys for signing.

---

## 4. Trust Boundaries

TB1. **Developer environment** (including Android/Termux)  
TB2. **Git hosting / remote repository** (push/tag integrity vs account compromise)  
TB3. **CI runner environment** (workflows, runners, secrets exposure)  
TB4. **Offline verifier environment** (validator correctness, policy selection)  
TB5. **Distribution / deployment pipeline** (registry, CDN, release assets, final mile)

Each boundary marks a shift in assumptions.

---

## 5. Attacker Profiles

P1. **Opportunistic external attacker**  
Attempts tampering, replay, or social engineering without insider access.

P2. **Malicious insider contributor**  
Can commit malicious code or manipulate process.

P3. **Compromised CI runner attacker**  
Can modify build outputs, inject artifacts, or exfiltrate secrets.

P4. **Private key attacker (key theft)**  
Obtains signing key material and produces valid-looking signatures.

P5. **Distribution attacker (artifact swap)**  
Swaps binaries/images after CI, before users deploy.

P6. **Policy manipulation attacker**  
Attempts to redefine “who is trusted” (allowed signers / trust anchor confusion).

---

## 6. Attack Surfaces

S1. **Private key storage / operational security**  
Device compromise, backups, malware, accidental exfiltration.

S2. **Git tag / release manipulation**  
Tag moves, forced pushes, release asset replacement.

S3. **CI supply chain compromise**  
Runner compromise, workflow changes, dependency poisoning.

S4. **Evidence pack tampering**  
Modifying tar contents, manifests, or included files.

S5. **Governance record tampering**  
Altering rotation/revocation records or bypassing enforcement.

S6. **Rollback / replay**  
Presenting an older valid bundle as “latest”.

S7. **Timestamp manipulation**  
Falsifying declared time without external anchor.

S8. **Deployment artifact replacement**  
CI was correct but deployed artifact differs.

---

## 7. Current Mitigations (V1)

M1. **Deterministic CI hash gate**  
CI produces a stable `CI_REPORT_V1` hash for the same state.

M2. **Reproducible Evidence Pack V2**  
Evidence bundle is content-derived and reproducible, with SHA256 manifest.

M3. **Offline verification**  
Bundle includes all required artifacts for validation without network access.

M4. **Governance rotation enforcement**  
Rotation records are signed and verified during validation.

M5. **Governance revocation enforcement**  
Revocation records are signed and verified; revoked keys are enforced by policy logic.

M6. **Core freeze discipline**  
The protocol surface is treated as frozen to prevent drift in trust semantics.

M7. **Artifact binding verification**  
Artifact manifest(s) ensure digest-level linkage between evidence pack and derived artifacts.

---

## 8. Residual Risks (Known Gaps)

R1. **Deployment tampering if deployed artifact digest is not enforced**  
If the final deployed binary/image digest is not bound and checked, the “last mile” can be swapped.

R2. **No external timestamp authority (declared time only)**  
Attestation time is a claim, not a public proof of existence at a given time.

R3. **Key compromise before revocation allows forged-but-valid signatures**  
If a key is stolen, signatures created before revocation appear valid.

R4. **1-of-1 governance (single point of failure)**  
Cryptographically valid but operationally centralized (no quorum safety).

R5. **Android/Termux operational risk if private keys are stored locally**  
Mobile devices increase compromise/exfiltration risk (malware, backups, screen capture, device loss).

R6. **Trust anchor ambiguity if bundle policy is not clearly defined**  
If “allowed signers” is taken from inside the bundle without an external policy model, self-validation critique applies.

R7. **Rollback/replay risk without monotonic release indexing**  
Older valid evidence may be replayed as “latest” without an anti-rollback signal.

R8. **CI runner compromise producing valid-looking but malicious outputs**  
A compromised runner can emit consistent hashes for malicious outputs if it controls the build process.

---

## 9. Non-Goals

ISC Core is not:

- A blockchain
- A distributed consensus network
- A public timestamp authority
- A hardware root-of-trust system
- A guarantee of software behavioral correctness

ISC Core provides cryptographic integrity + enforceable lifecycle rules, not absolute correctness or consensus truth.

---

## 10. Security Posture Summary (V1)

ISC Core guarantees deterministic build integrity, tamper-evident packaging, signed attestations, and enforceable governance lifecycle controls.

ISC Core assumes private key security and a clearly defined trust anchor / policy model.

External time anchoring, multi-party quorum governance, hardware-backed keys, and deployment digest enforcement are future hardening paths and are not part of V1 guarantees.

---

## 11. Threat-Driven Roadmap (Ordered)

1. Clarify policy trust anchor model (operator policy vs bundle snapshot)
2. Add anti-rollback / monotonic release index
3. Enforce deployment artifact digest binding
4. Improve key operational security (hardware-backed keys or dedicated environment)
5. Optional external timestamp anchoring
6. Future multi-signer quorum governance
