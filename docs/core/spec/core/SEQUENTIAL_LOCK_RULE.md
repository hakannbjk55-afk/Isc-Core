---
state: DRAFT
version: v1
---

# ISC-CORE SEQUENTIAL LOCK RULE

This document defines the canonical upstream/downstream locking rule for the ISC Core repository.

It enforces strict sequential stabilization:
downstream documents MUST NOT advance beyond the maturity state of their upstream documents.

This is a protocol governance contract, not an implementation guide.

---

## 1. Scope

This rule applies to all normative documents under:

- `docs/`
- `spec/`

It does NOT apply to:

- source code under `core/`
- tools under `tools/`
- golden vectors under `vectors/`

---

## 2. Definitions

### 2.1 Canonical Order List

The canonical upstream ordering list is defined in:

- `docs/core/ROADMAP.md`

This list is the single source of truth.

### 2.2 Upstream / Downstream

For any document path `D` in the canonical list:

- `upstream(D)` is the set of all documents listed earlier than `D`.
- `downstream(D)` is the set of all documents listed later than `D`.

No other upstream definition is valid.

### 2.3 State(D)

`state(D)` is the lifecycle state declared in YAML frontmatter of document `D`.

Valid values are:

- `DRAFT`
- `HARDENED`
- `FROZEN`

If the state is missing, the repository is invalid.

---

## 3. Sequential Lock Rule (Hard Gate)

### 3.1 Lock Principle

A document MUST NOT advance beyond the maturity of any upstream document.

This rule is absolute and MUST be enforced by CI.

### 3.2 Formal Rule

For any document `D`:

- If any `U` in `upstream(D)` has `state(U) = DRAFT`,
  then `state(D)` MUST be `DRAFT`.

- If any `U` in `upstream(D)` has `state(U) = HARDENED`,
  then `state(D)` MUST NOT be `FROZEN`.

Equivalently:

- `state(D) >= HARDENED` implies all upstream documents are at least HARDENED.
- `state(D) = FROZEN` implies all upstream documents are FROZEN.

---

## 4. Allowed State Combinations

The following combinations are valid:

- All documents are `DRAFT`.
- Some upstream documents are `HARDENED`, downstream remain `DRAFT`.
- A contiguous prefix of documents is `FROZEN`, and the rest are `DRAFT` or `HARDENED`.
- A contiguous prefix is `FROZEN`, followed by a contiguous block of `HARDENED`,
  followed by only `DRAFT`.

The following pattern MUST NOT occur:

- a downstream document in a higher state than an upstream document.

---

## 5. CI Enforcement Requirements

CI MUST enforce the sequential lock rule.

### 5.1 Mandatory CI Fail Conditions

CI MUST fail if any of the following is true:

- A document listed in `docs/core/ROADMAP.md` does not exist.
- A document exists but has missing YAML frontmatter.
- A document has missing `state`.
- A document has missing `version`.
- A document has unknown `state` value.
- Any downstream document is in a higher state than an upstream document.

### 5.2 Monotonicity Constraint

When traversing the canonical roadmap list in order:

- states MUST be non-increasing.

Valid sequences include:

- `DRAFT, DRAFT, DRAFT`
- `HARDENED, DRAFT, DRAFT`
- `FROZEN, HARDENED, DRAFT`
- `FROZEN, FROZEN, HARDENED, DRAFT`

Invalid sequences include:

- `DRAFT, HARDENED`
- `HARDENED, FROZEN`
- `DRAFT, FROZEN`

---

## 6. Drift Prevention Rule

### 6.1 Roadmap Ordering Consistency

If the canonical document order differs between:

- `docs/core/INDEX.md`
- `docs/core/ROADMAP.md`

CI MUST fail.

### 6.2 New Document Insertion

If a new document is inserted into the canonical list:

- it MUST begin in `DRAFT`
- all downstream documents MUST remain `DRAFT` until the new document reaches `HARDENED`

This prevents bypassing upstream stability requirements.

---

## 7. Failure Modes

This repository MUST reject the following failure modes:

- silent skipping of upstream documents
- missing documents in the canonical chain
- implied state inference based on directory
- state regression
- partial freezing of downstream documents while upstream is unstable

---

## 8. Final Rule

Sequential lock is not a guideline.

It is a hard gate.

If this rule is violated, the ISC Core genome becomes unstable.