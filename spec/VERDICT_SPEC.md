---
state: DRAFT
version: v1.3
---

# ISC-CORE VERDICT SPEC

This document defines the canonical verdict evaluation contract for ISC Core.

It specifies how external artifacts MUST be evaluated, how deterministic verdicts MUST be produced, and how stable verdict hashes MUST remain reproducible across independent receivers.

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/core/STATE_MACHINE.md
- spec/core/SEQUENTIAL_LOCK_RULE.md
- spec/core/DOC_FORMAT.md
- spec/core/PROTOCOL_MANIFEST.md

---

## 1. Purpose

The ISC Core repository is treated as a frozen genome.

Therefore:

- evaluation MUST be deterministic
- verdict outputs MUST be reproducible
- ambiguous interpretation MUST be treated as a failure condition
- stable output hashes MUST be environment-independent
- all canonical hash algorithms MUST be explicitly specified

---

## 2. Scope

This specification governs:

- receiver evaluation of artifacts
- dependency resolution behavior
- verdict output structure
- stable vs audit fields
- canonical hash computation rules

This specification does NOT define:

- implementation code architecture
- internal receiver storage layout
- UI rendering of verdicts

---

## 3. Definitions

### 3.1 Artifact

An artifact is any input object evaluated by a receiver.

Artifacts may include:

- markdown documents
- protocol specs
- test vector bundles
- patches
- structured metadata payloads

### 3.2 Receiver

A receiver is any system that evaluates an artifact and produces a verdict.

### 3.3 Verdict

A verdict is the final classification of an artifact under the ISC Core governance contract.

Verdict values are:

- ACCEPT
- REJECT
- QUARANTINE

### 3.4 Deterministic Completion

Deterministic completion means:

- identical artifact bytes
- identical declared dependencies
- identical dependency snapshots
- identical ruleset version
- identical time-source inputs (when applicable)

MUST yield identical verdict and identical stable verdict_hash.

---

## 4. Canonical Pipeline (Mandatory Order)

Receivers MUST evaluate artifacts using the following pipeline order.

No step MAY be skipped.

1. Artifact byte ingestion
2. Canonical byte normalization (DOC_FORMAT)
3. Metadata extraction
4. Dependency extraction
5. Dependency snapshot resolution
6. Ordering + reorder enforcement
7. TTL evaluation (if applicable)
8. Rule evaluation + validation
9. Verdict output emission

If any step fails to complete deterministically, the receiver MUST produce QUARANTINE or REJECT as defined by this spec.

---

## 5. Stable vs Audit Fields

### 5.1 Stable Fields

Stable fields MUST affect verdict_hash.

Stable fields MUST be fully deterministic.

Stable fields MUST NOT contain environment-dependent identifiers.

### 5.2 Audit Fields

Audit fields MUST NOT affect verdict_hash.

Audit fields MAY contain timestamps, file paths, runtime traces, and receiver-local diagnostics.

---

## 6. Artifact Metadata Contract

### 6.1 Artifact Type

Each artifact MUST declare its type explicitly.

Artifact type inference MUST NOT be used.

If artifact_type is absent, the receiver MUST REJECT.

### 6.2 Metadata Location Canonicalization

Metadata MUST be stored in one of the following canonical locations:

- Markdown artifacts MUST use YAML frontmatter.
- Non-markdown artifacts MUST use a sidecar metadata file named:
  `<artifact_name>.meta.yaml`

If metadata cannot be extracted from the canonical location, the receiver MUST QUARANTINE (Q150).

### 6.3 time_sensitive Flag

Each artifact MUST declare:

- time_sensitive: true|false

If absent:

- in DRAFT receiver MAY warn
- in HARDENED receiver MUST QUARANTINE (Q150)
- in FROZEN receiver MUST REJECT

---

## 7. Verdict Types

### 7.1 ACCEPT

ACCEPT MUST only be returned if:

- no rule violation exists
- dependency resolution succeeded deterministically
- reorder constraints are satisfied
- TTL is not expired (if applicable)
- canonical bytes are parse-safe
- no QUARANTINE trigger applies

### 7.2 REJECT

REJECT MUST be returned if:

- canonical bytes are invalid under DOC_FORMAT
- required metadata fields are missing (artifact_type, versioning fields, etc.)
- dependency cycles are detected
- TTL expired under verifiable time source
- a MUST/SHALL rule is violated

### 7.3 QUARANTINE

QUARANTINE MUST be returned if evaluation cannot safely complete deterministically.

QUARANTINE MUST NOT be used as a catch-all.

QUARANTINE MUST only be returned under enumerated trigger codes defined in Section 11.

---

## 8. Dependency Contract

### 8.1 Dependency Declaration

Each artifact MUST declare dependencies explicitly, even if empty.

The dependency declaration MUST be machine-readable.

If dependency declaration is absent:

- in DRAFT receiver SHOULD warn
- in HARDENED receiver MUST fail evaluation (Q120)
- in FROZEN receiver MUST REJECT

### 8.2 Dependency Schema

Dependencies MUST be expressed as a machine-readable list.

Dependency list semantics MUST be order-insensitive.
Receivers MUST NOT treat author-provided list order as meaningful.

Each dependency entry MUST contain:
- path (string)
- version (string)

Canonical form MUST be:

```yaml
dependencies:
  - path: spec/core/STATE_MACHINE.md
    version: v1.0
  - path: spec/core/SEQUENTIAL_LOCK_RULE.md
    version: v1.1

If dependencies exist but are malformed, receiver MUST QUARANTINE (Q120).

### 8.3 Dependency Version Resolution

Dependency versions MUST be exact.

Version ranges MUST NOT be used.

If a dependency version cannot be resolved exactly, receiver MUST QUARANTINE (Q120).

If multiple versions satisfy the same declared dependency (ambiguity), receiver MUST REJECT.