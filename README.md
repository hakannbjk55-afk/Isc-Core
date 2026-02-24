# ISC Core

ISC Core is a deterministic, tamper-evident, governance-enforced evidence engine.

It produces reproducible CI reports and cryptographically bound Evidence Packs
that can be verified offline. The core protocol surface is frozen under a
“frozen genome” discipline to preserve long-term integrity guarantees.

ISC Core is not a blockchain. It is a cryptographic evidence boundary system.

---

## Problem Statement

Modern CI/CD systems can produce artifacts, but they rarely provide:

- Deterministic reproducibility guarantees
- Cryptographically enforceable governance lifecycle
- Offline-verifiable release evidence
- Tamper-evident artifact binding

ISC Core addresses integrity — not consensus.

---

## What ISC Core Is

ISC Core provides:

- Deterministic CI report generation (`ci_report.json`)
- Stable CI hash commitment (`CI_REPORT_V1`)
- Reproducible Evidence Pack V2 (`evidence_pack_v2.tar`)
- Signed attestations (Ed25519)
- Governance lifecycle enforcement (rotation + revocation)
- Artifact binding manifests linking evidence to produced artifacts
- Offline verification capability

The protocol surface under `core/` is frozen.
All evolution occurs in modular layers (tools/, modules/, docs/, policy).

---

## What ISC Core Is Not

ISC Core is NOT:

- A blockchain
- A distributed consensus network
- A public timestamp authority
- A hardware root-of-trust system
- A guarantee of behavioral correctness of software
- A substitute for key management discipline

---

## Security Guarantees (V1)

ISC Core guarantees:

- Deterministic build integrity
- Tamper-evident packaging
- Signed attestations
- Governance rotation enforcement
- Governance revocation enforcement
- Offline verification of evidence packs
- Artifact binding validation

Security depends on:

- Private key operational security
- Clearly defined policy trust anchors

---

## Threat Model

Formal threat model:
docs/THREAT_MODEL_V1.md

The threat model defines:

- Protected assets
- Attacker profiles
- Trust boundaries
- Mitigations
- Residual risks
- Explicit non-goals

Development is threat-driven, not feature-driven.

---

## Architecture Overview

Core Layers:

1. Deterministic CI Engine
2. Evidence Pack Builder (V1/V2)
3. Governance Layer (rotation + revocation)
4. Artifact Binding Layer
5. Verification Tooling (offline capable)

All cryptographic boundaries are SHA256 + Ed25519 based.

---

## Verification Model

Verification enforces:

- Archive SHA256 integrity
- Signature validity
- Governance rotation signature
- Governance revocation signature
- Artifact binding validation
- Deterministic CI report hash consistency

Verification can be executed fully offline.

---

## Governance Model

Current model (V1):

- Single-signer governance (1-of-1)
- Signed rotation records
- Signed revocation records
- Enforced validation gates

Future hardening paths:

- Multi-signer quorum governance
- Hardware-backed key storage
- External time anchoring
- Deployment digest enforcement
- Monotonic release indexing

---

## Development Discipline

ISC Core follows:

- Frozen core protocol surface
- Deterministic CI gates
- Hash stability enforcement
- Cryptographic boundary preservation
- Threat-driven roadmap

Breaking protocol guarantees requires explicit version evolution.

---

## Roadmap (Threat-Driven)

1. Clarify trust anchor policy model
2. Anti-rollback / monotonic release index
3. Deployment artifact digest enforcement
4. Key operational hardening
5. Optional external timestamp anchoring
6. Optional multi-signer governance quorum

---

## Philosophy

ISC Core prioritizes integrity over distribution.
It enforces cryptographic boundaries over social trust.
It is minimal by design.

Integrity first.
Consensus optional.
Complexity controlled.

