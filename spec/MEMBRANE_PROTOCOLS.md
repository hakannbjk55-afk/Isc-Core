---
state: DRAFT
version: v1
---

# ISC-CORE MEMBRANE PROTOCOLS SPEC

This document defines the canonical membrane protocol layer for ISC Core.

The membrane is the boundary between external Producers and an ISC Receiver.

It specifies how artifacts MUST be submitted, identified, validated, and admitted into deterministic evaluation without allowing transport-level ambiguity to affect stable hashing.

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/core/PROTOCOL_MANIFEST.md
- spec/CANONICALIZATION.md
- spec/VERDICT_SPEC.md
- spec/ERROR_CODES.md
- spec/EVIDENCE_BLOB.md

---

## 1. Purpose

ISC Core is treated as a frozen genome.

Therefore:

- artifact admission MUST be deterministic
- transport MUST NOT influence canonical bytes
- envelope metadata MUST NOT drift into stable identity
- ambiguous or lossy submission MUST be treated as failure
- artifact lineage MUST be protected from replay and reorder ambiguity

This document defines the canonical "entry gate" rules.

---

## 2. Scope

This specification governs:

- artifact submission envelope requirements
- artifact admission rules
- transport-agnostic packaging constraints
- canonical artifact naming and path rules
- receiver intake validation requirements
- replay and duplication handling rules
- quarantine admission triggers

This specification does NOT define:

- specific network protocols (HTTP, gRPC, WebSocket)
- authentication or identity systems
- encryption or signature schemes
- UI submission workflows

---

## 3. Definitions

### 3.1 Membrane

The membrane is the deterministic boundary layer between external producers and an ISC receiver.

The membrane controls what is admissible for evaluation.

### 3.2 Envelope

An envelope is a transport-level container that wraps an artifact submission.

Envelope fields are audit-only unless explicitly defined as stable.

### 3.3 Submission Unit

A submission unit is the minimal object admitted into evaluation.

A submission unit contains:

- artifact bytes
- artifact metadata bytes
- optional evidence blobs
- optional submission envelope

### 3.4 Admission

Admission is the process of accepting a submission unit into the evaluation pipeline.

Admission MUST occur before canonicalization and verdict evaluation.

---

## 4. Admission Principles

### 4.1 Transport Independence

Transport MUST NOT affect:

- canonical bytes
- artifact_hash
- evidence_id
- dependency_snapshot_hash
- verdict_hash

Any transport-dependent variance MUST be rejected.

### 4.2 Deterministic Intake

A receiver MUST treat identical submission units as identical, regardless of:

- submission channel
- timing of arrival
- network framing
- chunking or streaming

### 4.3 No Implicit Metadata

Receivers MUST NOT infer missing metadata fields from envelope fields.

If required metadata is absent, receiver MUST REJECT (E160).

---

## 5. Submission Envelope Contract

### 5.1 Envelope Allowed Fields

An envelope MAY include:

- submission_id (audit-only)
- producer_id (audit-only)
- submitted_at_utc (audit-only)
- transport_ref (audit-only)
- notes (audit-only)

Envelope fields MUST NOT affect stable hashing.

### 5.2 Forbidden Envelope Influence

Receivers MUST NOT include envelope fields in:

- artifact_identity_bytes
- evidence_canonical_bytes
- dependency snapshot computation
- verdict_hash input object

If a receiver cannot separate envelope fields from stable identity:

- receiver MUST REJECT (E400)

---

## 6. Artifact Submission Requirements

### 6.1 Artifact Bytes

Artifact bytes MUST be provided exactly.

Receivers MUST NOT accept artifacts where bytes are reconstructed from:

- base64 fields inside JSON envelopes
- line-wrapped text fields
- lossy encodings

If submission format is lossy or ambiguous:

- receiver MUST REJECT (E120)

### 6.2 Metadata Bytes

Metadata MUST be submitted as canonical metadata bytes.

Rules:

- markdown artifacts MUST include YAML frontmatter inside the artifact bytes
- non-markdown artifacts MUST include `<artifact>.meta.yaml` bytes

If metadata bytes are missing:

- receiver MUST REJECT (E160)

### 6.3 Artifact Path Declaration

Each submission MUST declare an artifact_path.

artifact_path MUST follow spec/CANONICALIZATION.md path rules.

artifact_path MUST be treated as stable identity only if explicitly required by an upstream spec.

If artifact_path is malformed:

- receiver MUST REJECT (E130)

---

## 7. Evidence Submission Rules

### 7.1 Evidence Embedding

Evidence blobs MAY be submitted alongside artifacts.

If evidence is embedded, receiver MUST validate:

- evidence_id matches bytes
- evidence size matches manifest

If validation fails:

- receiver MUST REJECT (E302)

### 7.2 Missing Evidence Handling

If evidence is declared in manifest but not present:

- receiver MUST QUARANTINE (Q120)

If receiver refuses due to resource limits:

- receiver MUST QUARANTINE (Q140)

### 7.3 Evidence Transfer Independence

Evidence submission transport MUST NOT affect evidence bytes.

If evidence bytes are modified by transfer encoding:

- receiver MUST REJECT (E302)

---

## 8. Replay and Duplication Handling

### 8.1 Duplicate Submission

If a receiver receives a submission unit whose artifact_hash is already known:

- receiver MUST treat it as a duplicate submission

Duplicate submissions MUST NOT produce divergent outputs.

### 8.2 Duplicate Verdict Rule

If identical artifact_hash is evaluated under the same ruleset_id and dependency snapshot:

- receiver MUST output the identical verdict_hash

### 8.3 Replay as Audit Signal

Receivers MAY emit audit-only fields indicating replay detection.

Replay detection MUST NOT affect stable outputs.

---

## 9. Submission Ordering and Reorder

### 9.1 Ordering State

Receivers MUST maintain a deterministic ordering state.

Ordering state MUST be derived only from:

- previously admitted artifact hashes
- dependency snapshot states
- explicit reorder rules defined upstream

### 9.2 Out-of-Order Submission

If a submission arrives out-of-order:

- receiver MUST QUARANTINE (Q130)

Receivers MUST NOT accept out-of-order submissions unless reorder_window explicitly allows it.

---

## 10. Artifact Type Admission

### 10.1 Explicit Type Requirement

Every submission MUST include artifact_type in canonical metadata bytes.

Artifact type inference MUST NOT be used.

If artifact_type is missing:

- receiver MUST REJECT (E170)

If artifact_type is unknown:

- receiver MUST REJECT (E171)

### 10.2 Type-Based Admission Policies

Receivers MAY implement artifact_type-specific admission rules, but such rules MUST be defined by upstream frozen specs.

If admission rules are undefined:

- receiver MUST QUARANTINE (Q160)

---

## 11. Canonical Submission Unit Identity

### 11.1 Submission Identity Inputs

The stable identity of a submission unit MUST be derived only from:

- artifact_identity_bytes (as defined by PROTOCOL_MANIFEST)
- declared evidence_id list (sorted lexicographically)

Envelope fields MUST NOT affect submission identity.

### 11.2 Submission Identity Hash

Receivers MAY compute a submission_hash for deduplication.

If computed, submission_hash MUST be:

`sha256:<64 lowercase hex>`

Input MUST be canonical JSON using RFC 8785.

---

## 12. Failure Handling

### 12.1 Admission Failures

If admission cannot be performed deterministically:

- receiver MUST REJECT (E120)

### 12.2 Quarantine Admission Failures

QUARANTINE MUST only be used if:

- missing evidence blocks deterministic evaluation (Q120)
- reorder condition prevents deterministic admission (Q130)
- receiver resource limit prevents evaluation (Q140)

Any other intake ambiguity MUST be REJECT.

---

## 13. Compliance Requirements

A receiver is compliant with this spec only if it:

- isolates envelope fields from stable hashing
- enforces canonical metadata placement
- enforces canonical path rules
- produces deterministic deduplication behavior
- never accepts lossy transport submissions
- applies QUARANTINE only under allowed triggers

Any deviation MUST be treated as a governance violation.

---

## 14. Final Rule

Any ambiguity in membrane admission MUST be treated as a failure condition.

In DRAFT state, receiver MAY QUARANTINE if a canonical trigger exists.

In HARDENED and FROZEN state, ambiguous membrane admission MUST produce REJECT.