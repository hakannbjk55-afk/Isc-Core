
---
state: DRAFT
version: v1
---

# ISC-CORE EVIDENCE BLOB SPEC

This document defines the canonical evidence blob contract for ISC Core.

It specifies how external binary or structured evidence MUST be packaged, referenced, hashed, and verified in a deterministic and environment-independent manner.

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/CANONICALIZATION.md
- spec/VERDICT_SPEC.md
- spec/core/DOC_FORMAT.md
- spec/core/PROTOCOL_MANIFEST.md

---

## 1. Purpose

ISC Core treats accepted governance artifacts as part of a frozen genome.

Therefore, evidence MUST be:

- content-addressed
- immutable once referenced
- environment-independent
- reproducibly hashable
- safely transferable between receivers

Evidence blobs exist to prevent "trust-by-path" or "trust-by-storage" assumptions.

The only valid trust anchor for evidence is its canonical content address.

---

## 2. Scope

This specification governs:

- evidence blob identity rules
- evidence_id computation
- evidence manifest format
- evidence inclusion vs external reference rules
- deterministic evidence validation rules

This specification does NOT define:

- storage backends (S3, filesystem, IPFS, etc.)
- encryption schemes (unless explicitly referenced)
- network transport protocol details beyond canonical packaging

---

## 3. Definitions

### 3.1 Evidence Blob

An Evidence Blob is an immutable byte sequence that supports a governance decision.

Evidence blobs may include:

- binary captures
- log fragments
- replay traces
- screenshots or recordings
- compiled artifacts
- patch payloads
- zipped bundles
- structured JSON/YAML payloads

### 3.2 Evidence ID (evidence_id)

evidence_id is the canonical content address of an evidence blob.

evidence_id MUST be derived only from evidence_canonical_bytes.

evidence_id MUST be stable and deterministic across receivers.

### 3.3 Evidence Reference (evidence_ref)

An evidence_ref is a human- or system-usable pointer to evidence (path/URL/storage key).

evidence_ref is audit-only.

evidence_ref MUST NOT be used as a stable identifier.

### 3.4 Evidence Canonical Bytes (evidence_canonical_bytes)

evidence_canonical_bytes are the exact byte sequence used as hash input to compute evidence_id.

---

## 4. Canonical Evidence Identity Rules

### 4.1 Content Addressing Requirement

All evidence MUST be identified by its evidence_id.

Evidence MUST NOT be identified by:

- file path
- URL
- filename
- database ID
- storage bucket name
- timestamp-based naming

### 4.2 Canonical Evidence ID Format

evidence_id MUST be expressed as:

`sha256:<64 lowercase hex>`

No other formats are allowed.

If evidence_id is not canonical, the receiver MUST REJECT.

---

## 5. Evidence ID Computation

### 5.1 Canonical Bytes Rule

evidence_id MUST be computed from evidence_canonical_bytes.

The canonical byte rules are:

- for binary evidence blobs, evidence_canonical_bytes MUST be the exact raw evidence bytes
- for text evidence blobs, evidence_canonical_bytes MUST follow spec/CANONICALIZATION.md
- for structured evidence blobs stored as files (JSON/YAML), evidence_canonical_bytes MUST follow spec/CANONICALIZATION.md

Receivers MUST NOT perform implicit decoding, newline normalization, or compression normalization for binary evidence blobs.

If evidence canonicalization cannot be completed deterministically, receiver MUST REJECT.

### 5.2 Hash Algorithm

Evidence hash algorithm MUST be:

- SHA-256

The output MUST be lowercase hex.

### 5.3 Determinism Requirement

If two compliant receivers ingest identical evidence_canonical_bytes, they MUST compute identical evidence_id.

---

## 6. Evidence Manifest Contract

### 6.1 Manifest Requirement

If an artifact declares any evidence blobs, the artifact MUST include an evidence manifest.

The evidence manifest MUST be machine-readable.

### 6.2 Manifest Location

Evidence manifest MUST be stored in artifact metadata according to VERDICT_SPEC:

- Markdown artifacts MUST include the manifest in YAML frontmatter.
- Non-markdown artifacts MUST include the manifest in `<artifact_name>.meta.yaml`.

If evidence manifest is declared outside canonical metadata locations, receiver MUST REJECT.

### 6.3 Manifest Schema

Canonical schema:

```yaml
evidence:
  - evidence_id: "sha256:<64hex>"
    media_type: "application/octet-stream"
    size_bytes: 12345
    name: "optional_name.bin"
    description: "optional description"
Rules:
evidence MUST be a list (even if empty)
evidence_id MUST be canonical
size_bytes MUST be an integer >= 0
media_type MUST be a valid IANA media type string
name and description are audit-only
duplicate evidence_id entries are forbidden
If the evidence manifest is malformed, the receiver MUST REJECT.
7. Evidence Inclusion vs Reference
7.1 Evidence Modes
Evidence MAY be:
embedded inside a bundle artifact (if a bundle format defines embedding)
referenced externally by evidence_id
7.2 External Reference Rule
If evidence is not embedded, the artifact MUST still declare its evidence_id in the manifest.
Receivers MUST treat missing evidence bytes as an evaluation failure.
If evidence is declared but bytes are unavailable:
receiver MUST QUARANTINE (Q120) if evidence is required for deterministic evaluation
receiver MUST QUARANTINE (Q140) if the receiver refuses due to explicit resource limit
If evidence is declared but its computed evidence_id does not match:
receiver MUST REJECT
8. Evidence Storage Independence
8.1 Receiver Storage Independence
Receivers MAY store evidence blobs in any backend.
However, storage location MUST NOT affect:
evidence_id
artifact_hash
dependency_snapshot_hash
verdict_hash
8.2 evidence_ref Audit Field
Receivers MAY output an evidence_ref such as:
local filesystem path
S3 URL
internal database key
evidence_ref MUST be audit-only.
evidence_ref MUST NOT be used in stable hashing.
9. Evidence Use in Verdict Output
9.1 Evidence Fields
If a verdict references evidence, the verdict output MUST include:
Stable fields:
evidence_id (if required by the evaluation context)
Audit fields:
evidence_ref (optional)
9.2 Stable Hash Rule
Evidence MUST NOT be represented by path, URL, or filename in any stable hashing input.
Only evidence_id is permitted.
10. Evidence Size Rules
10.1 Size Declaration
If evidence is declared, size_bytes MUST be declared.
If the actual evidence size differs from size_bytes:
receiver MUST REJECT
10.2 Receiver Resource Limits
ISC Core does not impose a universal maximum evidence blob size.
Receivers MAY enforce resource limits.
If a receiver refuses evaluation due to evidence size limits:
receiver MUST QUARANTINE (Q140)
The receiver MUST emit an audit field describing the limit.
11. Evidence Compression Rules
11.1 Compression as Evidence
Compressed evidence is treated as raw evidence bytes.
Receivers MUST NOT attempt to normalize compression output.
If the blob is a zip/tar/gzip file:
evidence_id MUST be computed over the exact compressed bytes
11.2 Decompression for Evaluation
If a receiver must decompress evidence to evaluate it:
decompression MUST be treated as evaluation logic
the decompressed bytes MUST NOT redefine evidence_id
Only the original evidence_canonical_bytes define evidence_id.
12. Structured Evidence Interpretation
12.1 JSON Evidence Interpretation
If an evidence blob is declared as JSON and evaluation requires interpreting it:
receiver MAY parse it as JSON for evaluation purposes
parsing MUST be deterministic
Parsing or interpretation MUST NOT redefine evidence_id.
If a stable hash is required for the interpreted JSON object, the upstream spec requiring it MUST define an explicit RFC 8785 hashing rule.
12.2 YAML Evidence Interpretation
YAML evidence MUST NOT be used as a stable structured evaluation input unless explicitly converted to canonical JSON by an upstream spec.
If YAML evidence is used:
it MUST be treated as raw bytes evidence only
it MUST NOT affect stable hash-based evaluation unless explicitly converted into canonical JSON form
13. Evidence Ordering Rules
13.1 Manifest Ordering
The evidence manifest list MUST be treated as order-insensitive.
Receivers MUST normalize manifest ordering by sorting entries by evidence_id lexicographically.
13.2 Duplicate Evidence IDs
Duplicate evidence_id entries are forbidden.
If duplicates exist:
receiver MUST REJECT
14. Evidence Integrity Validation
14.1 Required Validation
Receivers MUST validate:
evidence blob SHA-256 matches evidence_id
evidence blob size matches size_bytes
If validation fails:
receiver MUST REJECT
14.2 Missing Evidence
If evidence is declared but bytes are missing:
receiver MUST QUARANTINE (Q120)
15. Evidence and Dependency Snapshots
Evidence MUST NOT be treated as a dependency document unless explicitly declared as such.
Evidence blobs MUST NOT be allowed to modify dependency resolution rules.
16. Determinism Guarantees
If two compliant receivers ingest:
identical artifact canonical bytes
identical evidence blobs
identical dependency versions
Then both receivers MUST compute identical:
evidence_id values
artifact_hash
dependency_snapshot_hash
verdict_hash
17. Backward Compatibility
Once FROZEN:
evidence_id format MUST NOT change
hash algorithm MUST NOT change
Any semantic change MUST be introduced via a new versioned spec path.
18. Compliance Requirements
A receiver is compliant with this spec only if it:
computes evidence_id using SHA-256
treats evidence_id as the only stable identifier
validates evidence bytes against evidence_id
rejects malformed evidence manifests
normalizes manifest ordering deterministically
never uses evidence_ref in stable hashing
Any deviation MUST be treated as a governance violation.
19. Final Rule
Any ambiguity in evidence identity MUST be treated as a failure condition.
If evidence identity cannot be determined deterministically:
receiver MUST REJECT
If evidence is declared but unavailable:
receiver MUST QUARANTINE (Q120) or QUARANTINE (Q140) depending on the failure class
In FROZEN state, ambiguity MUST produce REJECT.
