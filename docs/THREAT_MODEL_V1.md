# ISC Core — Threat Model V1

## 1. System Overview

ISC Core is a deterministic, tamper-evident, governance-enforced evidence engine.

It produces reproducible CI reports and evidence bundles (Evidence Pack V2) that can be verified offline.  
The core protocol is frozen (“frozen genome” discipline).  
All extensions (time layer, governance, artifact binding) are modular and versioned.

ISC Core does not aim to provide consensus, distributed trust, or external timestamp authority.  
It provides cryptographic integrity and enforceable evidence boundaries.

---

## 2. Protected Assets

A1. Repository State Integrity  
Source code and specifications that define the system state.

A2. Deterministic CI Outputs  
CI report (`ci_report.json`) and CI_REPORT_V1 hash stability.

A3. Evidence Pack Integrity  
`evidence_pack_v2.tar`, manifest files, and included artifacts.

A4. Governance Records  
`rotation_commit.json`, `revocation_record.json`, associated hashes and signatures.

A5. Release Attestations  
Signed attestation objects and declared timestamps.

A6. Artifact Binding  
Artifact manifest linking evidence pack and derived artifacts.

A7. Signing Keys  
Private keys used for attestation and governance.

---

## 3. Trust Boundaries

TB1. Developer Environment (including Android/Termux)  
TB2. Git hosting / remote repository  
TB3. CI runner environment  
TB4. Offline verifier environment  
TB5. Distribution / deployment pipeline  

Each boundary represents a location where trust assumptions change.

---

## 4. Attacker Profiles

P1. Opportunistic external attacker  
P2. Malicious insider contributor  
P3. Compromised CI runner  
P4. Private key attacker (key theft)  
P5. Distribution attacker (artifact swap)  
P6. Policy manipulation attacker  

---

## 5. Attack Surfaces

S1. Private key storage and operational security  
S2. Git tag / release manipulation  
S3. CI workflow supply chain compromise  
S4. Evidence pack tampering  
S5. Governance record tampering  
S6. Rollback / replay attacks  
S7. Timestamp manipulation  
S8. Deployment artifact replacement  

---

## 6. Current Mitigations

M1. Deterministic CI hash gate  
M2. Reproducible Evidence Pack V2 + SHA256 manifest  
M3. Offline verification  
M4. Governance rotation signature enforcement  
M5. Governance revocation signature enforcement  
M6. Core freeze discipline  
M7. Artifact binding manifest verification  

---

## 7. Residual Risks

R1. Deployment tampering if deployed artifact digest is not enforced  
R2. No external timestamp authority (declared time only)  
R3. Key compromise before revocation allows forged but valid signatures  
R4. 1-of-1 governance (single point of failure)  
R5. Android/Termux operational risk if private keys are stored locally  
R6. Trust anchor ambiguity if bundle policy is not clearly defined  
R7. Rollback/replay risk without monotonic release indexing  
R8. CI runner compromise producing valid-looking but malicious outputs  

---

## 8. Non-Goals

ISC Core is not:

- A blockchain
- A distributed consensus network
- A public timestamp authority
- A hardware root-of-trust system
- A guarantee of software behavioral correctness

---

## 9. Security Posture Summary

ISC Core guarantees deterministic build integrity, tamper-evident packaging, signed attestations, and enforceable governance lifecycle controls.

It assumes private key security and trusted policy definitions.

External time anchoring, multi-party quorum governance, hardware-backed keys, and deployment digest enforcement are future hardening paths and not part of V1 guarantees.

---

## 10. Threat-Driven Roadmap

1. Clarify policy trust anchor model  
2. Add anti-rollback / monotonic release index  
3. Enforce deployment artifact digest binding  
4. Improve key operational security (hardware-backed keys or dedicated environment)  
5. Optional external timestamp anchoring  
6. Future multi-signer quorum governance  

