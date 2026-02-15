
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

ISC Core treats all accepted governance artifacts as part of a frozen genome.

Therefore, evidence MUST be:

- content-addressed
- immutable once referenced
- environment-independent
- reproducibly hashable
- safely transferable between receivers

Evidence blobs exist to prevent "trust-by-path" or "trust-by-storage" assumptions.

The only valid trust anchor for evidence is its canonical hash.

---

## 2. Scope

This specification governs:

- evidence blob structure
- evidence hash computation
- evidence referencing rules
- evidence manifest rules
- evidence inclusion rules for artifacts and verdicts
- deterministic decoding and validation rules

This specification does NOT define:

- storage backends (S3, filesystem, IPFS, etc.)
- encryption schemes (unless explicitly referenced)
- transport protocol details beyond canonical packaging

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

### 3.2 Evidence Hash

Evidence hash is the canonical content address of an evidence blob.

It MUST be derived only from canonical bytes.

### 3.3 Evidence Reference (evidence_ref)

An evidence_ref is a human- or system-usable pointer to evidence.

evidence_ref is audit-only.

It MUST NOT be used as a stable identifier.

### 3.4 Evidence Identifier (evidence_id)

An evidence_id is the canonical stable reference to evidence.

It MUST be content-addressed.

It MUST be deterministic.

---

## 4. Canonical Evidence Identity Rules

### 4.1 Content Addressing Requirement

All evidence MUST be identified by its hash.

Evidence MUST NOT be identified by:

- file path
- URL
- filename
- database ID
- storage bucket name
- timestamp-based naming

### 4.2 Canonical Evidence ID Format

evidence_id MUST be expressed as:

sha256:<64 lowercase hex>

No other formats are allowed.

If evidence_id is not canonical, the receiver MUST REJECT.

---

## 5. Evidence Hash Computation

### 5.1 Canonical Bytes

Evidence hash MUST be computed from canonical bytes.

Canonical bytes MUST be defined as:

- the exact raw byte sequence of the evidence blob
- no implicit decoding
- no implicit newline normalization
- no implicit compression normalization

If the evidence blob is a structured artifact (JSON/YAML), canonicalization MUST follow `spec/CANONICALIZATION.md`.

### 5.2 Hash Algorithm

Evidence hash algorithm MUST be:

- SHA-256

The output MUST be lowercase hex.

### 5.3 Determinism Requirement

If two compliant receivers ingest identical evidence bytes, they MUST compute identical evidence_id.

---

## 6. Evidence Packaging Contract

### 6.1 Evidence Manifest

If an artifact contains multiple evidence blobs, the artifact MUST include an evidence manifest.

The evidence manifest MUST be machine-readable.

The manifest MUST declare:

- evidence_id
- media_type
- size_bytes
- optional name (audit-only)
- optional description (audit-only)

### 6.2 Manifest Location

If the artifact is a markdown document, the evidence manifest MUST be referenced in YAML frontmatter.

If the artifact is non-markdown, the evidence manifest MUST be stored in the canonical sidecar metadata file.

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
If the evidence manifest is malformed, the receiver MUST REJECT.
7. Evidence Inclusion vs Reference
7.1 Evidence Modes
Evidence MAY be:
embedded inside a bundle artifact
referenced externally by evidence_id
7.2 External Reference Rule
If evidence is not embedded, the artifact MUST still declare its evidence_id.
Receivers MUST treat missing evidence bytes as an evaluation failure.
If evidence is required for deterministic evaluation but is unavailable:
receiver MUST QUARANTINE (Q120)
If evidence is declared but its hash does not match:
receiver MUST REJECT
8. Evidence Blob Storage Rules
8.1 Receiver Storage Independence
Receivers MAY store evidence blobs in any backend.
However:
storage location MUST NOT affect:
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
9. Evidence Use in Verdict Evaluation
9.1 Evidence Hash Requirement
If a verdict references evidence, the verdict output MUST include:
evidence_id (stable)
evidence_ref (optional audit)
9.2 Verdict Stable Field Rule
If evidence is required for evaluation, evidence_id MUST be included in stable evaluation context.
Evidence MUST NOT be represented by path, URL, or filename.
10. Evidence Blob Size Rules
10.1 Size Declaration
If evidence is declared, size_bytes MUST be declared.
If the actual evidence size differs from size_bytes:
receiver MUST REJECT
10.2 Maximum Size Policy
ISC Core does not impose a universal maximum evidence blob size.
However, receivers MAY enforce resource limits.
If a receiver refuses evaluation due to evidence size limits:
receiver MUST QUARANTINE (Q140)
The receiver MUST emit an audit field describing the limit.
11. Evidence Compression Rules
11.1 Compression as Evidence
Compressed evidence is treated as raw evidence bytes.
Receivers MUST NOT attempt to normalize compression output.
If the blob is a zip/tar/gzip file:
its hash is computed over the exact compressed bytes
11.2 Decompression for Evaluation
If a receiver must decompress evidence to evaluate it:
decompression MUST be treated as evaluation logic
the decompressed bytes MUST NOT redefine evidence_id
Only the original raw evidence bytes define evidence_id.
12. Structured Evidence Canonicalization
12.1 JSON Evidence
If an evidence blob is declared as JSON and evaluation requires interpreting it:
the receiver MUST canonicalize JSON bytes using RFC 8785 rules as defined in spec/CANONICALIZATION.md.
12.2 YAML Evidence
YAML evidence MUST NOT be used as stable evidence unless converted to canonical JSON.
If YAML evidence is used:
it MUST be treated as raw bytes evidence only
it MUST NOT affect stable hash-based evaluation unless explicitly converted into canonical JSON form
13. Evidence Ordering Rules
13.1 Manifest Ordering
The evidence manifest list MUST be treated as ordered-insensitive.
Receivers MUST normalize evidence list ordering by sorting by evidence_id lexicographically.
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
receiver MUST QUARANTINE or REJECT depending on the failure class
In FROZEN state, ambiguity MUST produce REJECT.
