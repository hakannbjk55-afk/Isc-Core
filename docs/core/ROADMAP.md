---
state: DRAFT
version: v1
---

# ISC Core — ROADMAP (Canonical Build Order)

This document defines the mandatory writing, hardening, and freezing order for ISC Core.

ISC Core is treated as a frozen genome.
Therefore, document stabilization MUST follow a strict sequential dependency order.

This file is a process governance contract, not a protocol spec.

This document is downstream of:

- docs/core/INDEX.md

---

## 1. Purpose

This roadmap exists to prevent governance drift.

It defines:

- the canonical build order
- the stabilization sequence
- the hardening checkpoints
- the freeze triggers
- the CI activation order

No downstream document may be finalized if upstream contracts are not stabilized.

---

## 2. Absolute Rule: Sequential Build Order

The ISC Core repository is a frozen genome.

Therefore:

- documents MUST be hardened sequentially
- no downstream document may advance beyond upstream maturity state
- any attempt to "skip ahead" MUST be treated as a governance violation

---

## 3. Canonical Build Order (Authoritative)

The following order is mandatory.

### 3.1 Core Governance Layer (`spec/core/`)

1. `spec/core/PROTOCOL_MANIFEST.md`
2. `spec/core/STATE_MACHINE.md`
3. `spec/core/SEQUENTIAL_LOCK_RULE.md`
4. `spec/core/DOC_FORMAT.md`

### 3.2 Core Protocol Contracts (`spec/`)

5. `spec/CANONICALIZATION.md`
6. `spec/VERDICT_SPEC.md`
7. `spec/EVIDENCE_BLOB.md`
8. `spec/ERROR_CODES.md`
9. `spec/MEMBRANE_PROTOCOLS.md`

---

## 4. Stabilization Phases

Each document MUST advance through these maturity phases:

- DRAFT
- HARDENED
- FROZEN

### 4.1 DRAFT

DRAFT means:

- the contract is incomplete
- ambiguity is still expected
- test vectors may be incomplete
- downstream documents may reference it, but MUST NOT be frozen

### 4.2 HARDENED

HARDENED means:

- all normative rules are complete
- no TODO placeholders are allowed
- all MUST/SHALL rules are explicit
- deterministic failure behavior is explicit
- required test vectors exist

### 4.3 FROZEN

FROZEN means:

- no semantic changes are allowed
- only formatting fixes are permitted (non-semantic)
- any semantic change requires a new version bump

---

## 5. Hardening Exit Criteria (DRAFT → HARDENED)

A document may advance from DRAFT to HARDENED only if:

- all normative rules are explicit
- ambiguity cases are enumerated
- null vs absent semantics are explicit where applicable
- canonical encoding rules are explicitly defined
- stable vs audit fields are explicitly separated
- test vectors exist for acceptance and rejection paths
- failure modes are deterministic

---

## 6. Freeze Exit Criteria (HARDENED → FROZEN)

A document may advance from HARDENED to FROZEN only if:

- CI enforces all critical invariants
- deterministic hash outputs are verified across environments
- no unresolved edge cases remain
- no conflicting downstream assumptions exist
- backward compatibility rules are explicit

---

## 7. CI Activation Timeline

CI enforcement MUST be activated in the same order as stabilization.

Receivers MUST NOT rely on rules that CI cannot enforce.

Minimum required CI checks by stage:

### 7.1 Stage 1: Canonicalization CI

Triggered when `spec/CANONICALIZATION.md` enters HARDENED.

CI MUST verify:

- newline normalization determinism
- NFC normalization determinism
- strict YAML validity checks
- canonical hash format enforcement

### 7.2 Stage 2: Verdict CI

Triggered when `spec/VERDICT_SPEC.md` enters HARDENED.

CI MUST verify:

- verdict_hash determinism using RFC 8785
- reason_codes normalization
- dependency_snapshot_hash determinism
- reorder handling determinism

### 7.3 Stage 3: Evidence CI

Triggered when `spec/EVIDENCE_BLOB.md` enters HARDENED.

CI MUST verify:

- evidence_id hashing correctness
- manifest ordering normalization
- evidence size validation behavior
- duplicate evidence_id rejection

### 7.4 Stage 4: Error Codes CI

Triggered when `spec/ERROR_CODES.md` enters HARDENED.

CI MUST verify:

- canonical namespace enforcement
- deterministic precedence mapping
- unknown code rejection behavior

### 7.5 Stage 5: Membrane CI

Triggered when `spec/MEMBRANE_PROTOCOLS.md` enters HARDENED.

CI MUST verify:

- envelope fields do not affect stable hashing
- lossy transport detection
- deterministic duplicate handling
- strict QUARANTINE trigger enforcement

---

## 8. Governance Lock Rule (Mandatory)

Downstream documents MUST NOT advance beyond upstream maturity state.

Formal rule:

For any document B depending on A:

`state(B) <= state(A)`

Violation MUST be treated as a governance failure.

---

## 9. Final Rule

ISC Core MUST remain deterministic, reproducible, and environment-independent.

Any ambiguity not explicitly resolved MUST be treated as a failure condition.