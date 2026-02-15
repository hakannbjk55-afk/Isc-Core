---
state: DRAFT
version: v1
---

# ISC-CORE MEMBRANE PROTOCOLS SPEC

This document defines the canonical membrane boundary protocols for ISC Core.

It specifies how artifacts cross the boundary between producer systems and receiver systems, and how transport, packaging, and envelope rules MUST preserve determinism.

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/core/DOC_FORMAT.md
- spec/core/PROTOCOL_MANIFEST.md
- spec/VERDICT_SPEC.md
- spec/CANONICALIZATION.md
- spec/EVIDENCE_BLOB.md

---

## 1. Purpose

The ISC Core repository is treated as a frozen genome.

Therefore:

- artifact transport MUST preserve canonical bytes
- packaging MUST be deterministic
- envelope metadata MUST be canonical
- boundary crossing MUST be reproducible across receivers
- receiver evaluation MUST NOT depend on filesystem layout or transport medium

This document defines the membrane rules that prevent "transport drift".

---

## 2. Scope

This specification governs:

- artifact transport envelopes
- packaging format rules
- bundle structure
- manifest requirements
- file naming rules
- cross-platform byte stability
- transport-layer metadata normalization

This specification does NOT define:

- cryptographic signing systems (unless explicitly required by other specs)
- network transport protocols (HTTP, S3, IPFS, etc.)
- implementation details of upload/download systems

---

## 3. Definitions

### 3.1 Membrane

The membrane is the canonical boundary between:

- Producer systems (emit artifacts)
- Receiver systems (evaluate artifacts)

The membrane is not a network.
The membrane is a deterministic transport contract.

### 3.2 Envelope

An envelope is a structured container that wraps one or more artifacts.

An envelope MUST provide:

- stable artifact identity
- stable byte inclusion
- stable manifest structure
- stable dependency declaration
- stable evidence binding references

### 3.3 Bundle

A bundle is a transport unit containing:

- a manifest file
- one or more artifacts
- optional evidence blobs

A bundle MUST be deterministic.

### 3.4 Transport Drift

Transport drift is any difference introduced by:

- OS filesystem normalization
- newline conversions
- archive tool differences
- filename case differences
- timestamp embedding
- non-deterministic ordering of files

Transport drift MUST be treated as a failure condition.

---

## 4. Canonical Bundle Format

### 4.1 Bundle Container

The canonical bundle container format MUST be:

- ZIP (store mode preferred, no compression requirement)

A receiver MAY support additional formats, but ZIP MUST be supported.

If a bundle is not ZIP, receiver MUST QUARANTINE unless explicitly allowed by policy.

### 4.2 Deterministic ZIP Requirements

If ZIP is used, the following MUST apply:

- file order inside the ZIP MUST be lexicographically sorted
- file timestamps inside ZIP headers MUST be set to a constant value
- no OS-specific attributes MUST be stored
- directory entries MUST NOT be included
- file permissions MUST be normalized
- compression method MUST be deterministic if used

If deterministic ZIP requirements are violated, receiver MUST QUARANTINE.

---

## 5. Canonical Bundle Structure

A bundle MUST contain:

- `manifest.json`
- `artifacts/` directory
- optional `evidence/` directory

Bundle root MUST NOT contain additional files.

### 5.1 Required Layout

bundle_root/ manifest.json artifacts/  evidence/ 

If layout is violated, receiver MUST REJECT.

---

## 6. manifest.json Contract

### 6.1 Required Fields

manifest.json MUST be a JSON object.

manifest.json MUST include:

- bundle_id
- bundle_version
- created_by
- created_time (audit only)
- artifacts (array)
- evidence (array, may be empty)
- ruleset_id
- dependency_snapshot_hash

### 6.2 Canonical Field Requirements

bundle_id MUST be stable and deterministic.

bundle_id MUST be expressed as:

- sha256:<64 lowercase hex>

bundle_id MUST be computed from:

- canonical manifest fields excluding audit fields

### 6.3 Audit Fields

created_time MUST be treated as audit-only.

created_time MUST NOT affect bundle_id or any stable hash.

---

## 7. Artifact Entry Schema

Each artifact entry in manifest.json MUST include:

- path
- artifact_hash
- artifact_type
- declared_version
- dependencies

### 7.1 Canonical Path Rules

path MUST be relative.

path MUST NOT contain:

- `..`
- absolute prefixes
- OS-specific separators

path MUST use `/` as separator.

path MUST be case-sensitive.

If a receiver environment cannot preserve case sensitivity, it MUST REJECT.

### 7.2 artifact_hash Rules

artifact_hash MUST follow:

- sha256:<64 lowercase hex>

artifact_hash MUST match the canonical bytes defined in DOC_FORMAT and CANONICALIZATION.

Mismatch MUST cause REJECT.

---

## 8. Evidence Entry Schema

Each evidence entry in manifest.json MUST include:

- path
- evidence_hash
- evidence_type
- size_bytes

### 8.1 evidence_hash Rules

evidence_hash MUST be:

- sha256:<64 lowercase hex>

Evidence MUST be content-addressed.

Evidence MUST NOT be referenced by URL, host path, or external environment identifier.

---

## 9. File Ordering Rules

### 9.1 Artifact Ordering

The artifacts array in manifest.json MUST be sorted lexicographically by:

- artifact path

### 9.2 Evidence Ordering

The evidence array in manifest.json MUST be sorted lexicographically by:

- evidence path

If ordering differs, receiver MUST QUARANTINE.

---

## 10. Canonical JSON Rules for manifest.json

manifest.json MUST be representable under RFC 8785 canonical JSON rules.

Receivers MUST compute all stable hashes using RFC 8785 bytes.

Whitespace MUST NOT affect stable hashes.

If manifest.json is not valid JSON, receiver MUST REJECT.

---

## 11. Bundle Hashes

### 11.1 bundle_id Computation

bundle_id MUST be computed from the Manifest Hash Input Object (MHI).

The MHI MUST contain only stable fields:

- ruleset_id
- dependency_snapshot_hash
- artifacts (canonical list)
- evidence (canonical list)

No audit fields are allowed.

### 11.2 Canonical Encoding

MHI MUST be encoded using RFC 8785.

bundle_id MUST be:

sha256( RFC8785(MHI) )

---

## 12. Receiver Extraction Rules

Receivers MUST extract bundles into a receiver-local sandbox.

Receivers MUST NOT rely on filesystem metadata.

Receivers MUST treat extracted bytes as authoritative.

If extraction modifies bytes (newline conversion, encoding conversion), receiver MUST REJECT.

---

## 13. Transport Layer Independence

A receiver MUST NOT use:

- download URL
- HTTP headers
- S3 object metadata
- filesystem timestamps
- OS file permissions

as stable evaluation inputs.

These MAY be recorded as audit fields only.

---

## 14. Filename Normalization Rules

Receivers MUST treat filenames as canonical bytes.

Receivers MUST NOT normalize:

- Unicode
- case
- whitespace
- separators (except enforcing `/` in manifest paths)

If a receiver platform auto-normalizes filenames, the receiver MUST QUARANTINE or REJECT depending on severity.

---

## 15. Cross-Platform Determinism Requirements

Receivers MUST produce identical bundle_id and artifact_hash values regardless of:

- OS
- CPU architecture
- filesystem type
- ZIP library implementation

If receiver cannot guarantee this, it MUST declare non-compliance.

---

## 16. Failure Classification

### 16.1 QUARANTINE Conditions

Receiver MUST QUARANTINE if:

- ZIP ordering is non-deterministic
- ZIP headers contain non-canonical timestamps
- manifest arrays are not sorted
- extraction tool cannot guarantee byte-preserving output

### 16.2 REJECT Conditions

Receiver MUST REJECT if:

- bundle layout is invalid
- manifest.json missing required fields
- artifact_hash mismatch
- evidence_hash mismatch
- invalid path traversal is detected
- manifest is not valid JSON

---

## 17. Determinism Guarantee

If two receivers are compliant with this spec, then identical bundle input bytes MUST yield identical:

- artifact_hash results
- evidence_hash results
- dependency_snapshot_hash values
- bundle_id values

Audit fields MAY differ.

---

## 18. Backward Compatibility

New bundle formats MUST be versioned.

Receivers MUST reject unknown bundle_version unless explicitly allowed by policy.

Frozen bundle_version semantics MUST NOT be modified.

---

## 19. Compliance Requirements

A receiver is compliant only if it:

- enforces canonical ZIP rules
- enforces canonical layout
- enforces manifest schema
- enforces RFC 8785 canonical JSON hashing
- enforces content-addressed evidence references
- rejects path traversal

Any deviation MUST be treated as a governance violation.

---

## 20. Final Rule

Any ambiguity not explicitly resolved by this document MUST be treated as a failure condition.

In DRAFT, failure MAY produce QUARANTINE.
In HARDENED, failure MUST produce QUARANTINE or REJECT depending on severity.
In FROZEN, ambiguity MUST produce REJECT.