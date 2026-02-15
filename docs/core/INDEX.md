---
state: DRAFT
version: v1
---

# ISC Core — INDEX

This document is the canonical entry point for the ISC Core repository.

ISC Core is treated as a frozen genome.
Therefore, the repository MUST define a stable set of normative governance contracts and a strict stabilization order.

This file defines:

- the authoritative document list
- the dependency order (canonical build order)
- the canonical meaning of "Core DNA"
- the minimal compliance reading path

This is a governance index, not an implementation guide.

---

## 1. Core Principle

ISC Core is a frozen genome.

Therefore:

- deterministic interpretation is mandatory
- canonical bytes and canonical hashing are mandatory
- ambiguity is treated as a protocol failure
- downstream documents MUST NOT advance beyond upstream maturity state

---

## 2. Canonical Document Set (Core DNA)

The following documents define the ISC Core DNA and MUST be treated as normative.

### 2.1 Core Governance Layer (`spec/core/`)

- `spec/core/PROTOCOL_MANIFEST.md`
- `spec/core/STATE_MACHINE.md`
- `spec/core/SEQUENTIAL_LOCK_RULE.md`
- `spec/core/DOC_FORMAT.md`

### 2.2 Core Protocol Layer (`spec/`)

- `spec/CANONICALIZATION.md`
- `spec/VERDICT_SPEC.md`
- `spec/EVIDENCE_BLOB.md`
- `spec/ERROR_CODES.md`
- `spec/MEMBRANE_PROTOCOLS.md`

---

## 3. Canonical Dependency Order

Documents MUST be read and stabilized in the following order.
Upstream documents define rules that downstream documents MUST follow.

### 3.1 Absolute Upstream Layer

1. `spec/core/PROTOCOL_MANIFEST.md`
2. `spec/core/STATE_MACHINE.md`
3. `spec/core/SEQUENTIAL_LOCK_RULE.md`
4. `spec/core/DOC_FORMAT.md`

### 3.2 Protocol Contracts Layer

5. `spec/CANONICALIZATION.md`
6. `spec/VERDICT_SPEC.md`
7. `spec/EVIDENCE_BLOB.md`
8. `spec/ERROR_CODES.md`
9. `spec/MEMBRANE_PROTOCOLS.md`

---

## 4. Mandatory Reading Path (Minimal Compliance)

A receiver implementer MUST read at minimum:

1. `spec/core/PROTOCOL_MANIFEST.md`
2. `spec/core/DOC_FORMAT.md`
3. `spec/CANONICALIZATION.md`
4. `spec/VERDICT_SPEC.md`
5. `spec/EVIDENCE_BLOB.md`
6. `spec/ERROR_CODES.md`

Any receiver claiming compliance without implementing these documents is non-compliant.

---

## 5. Document State Rules

Each normative document MUST declare:

- state
- version

Allowed states:

- DRAFT
- HARDENED
- FROZEN

Downstream documents MUST NOT advance beyond upstream state.

Formal rule:

For any document B depending on A:

`state(B) <= state(A)`

---

## 6. Core Compliance Guarantee

A system is considered ISC Core compliant only if:

- it enforces deterministic canonicalization
- it enforces deterministic verdict evaluation
- it validates evidence deterministically
- it enforces canonical reason codes
- it enforces membrane admission constraints

---

## 7. Final Rule

Any ambiguity in interpreting the ISC Core document set MUST be treated as a failure condition.

This repository MUST be treated as a deterministic governance contract set.