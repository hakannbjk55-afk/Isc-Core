state: DRAFT
version: v1
title: ISC-CORE CANONICALIZATION SPEC

# ISC-CORE CANONICALIZATION SPEC

This document defines the canonical byte normalization and canonical encoding rules for ISC Core.

It specifies how artifacts MUST be converted into stable canonical bytes so that independent receivers produce identical hashes, identical `verdict_hash` inputs, and identical dependency snapshots.

This is a protocol governance contract, not an implementation guide.

## Upstream / Downstream

This document is upstream of:
- `spec/VERDICT_SPEC.md`
- `spec/ERROR_CODES.md`
- `spec/EVIDENCE_BLOB.md`

This document is downstream of:
- `spec/core/DOC_FORMAT.md`
- `spec/core/PROTOCOL_MANIFEST.md`

---

## 1. Purpose

The ISC Core repository is treated as a frozen genome.

Therefore:

- canonicalization MUST be deterministic
- canonical bytes MUST be identical across environments
- canonical hashes MUST be reproducible
- ambiguous encoding MUST be treated as a failure condition
- canonical output MUST NOT depend on filesystem paths, OS defaults, locale, or tool versions

This document defines the canonical transformation rules that produce the only valid input bytes for hashing.

---

## 2. Scope

This specification governs:

- byte normalization rules for all artifact types
- canonical hash input bytes
- canonical JSON encoding rules for stable structured objects
- newline normalization requirements
- unicode normalization requirements
- deterministic failure handling rules

This specification does NOT define:

- how artifacts are fetched or stored
- network transport rules
- compression rules for bundles
- encryption or signature schemes
- signature verification rules

---

## 3. Definitions

### 3.1 Canonical Bytes

Canonical bytes are the exact byte sequence produced by applying the canonicalization pipeline defined in this document.

Canonical bytes MUST be used for all stable hashing operations.

### 3.2 Canonical Hash

A canonical hash is a SHA-256 hash computed over canonical bytes.

### 3.3 Canonical JSON (RFC 8785)

Canonical JSON refers to JSON encoded using the RFC 8785 JSON Canonicalization Scheme (JCS).

### 3.4 Environment-Independent

Environment-independent means canonical bytes MUST NOT vary based on:

- operating system (Windows/Linux/macOS)
- line endings
- filesystem encoding
- locale / language settings
- timezone settings
- JSON library output formatting
- runtime or platform differences

### 3.5 Text Artifact

A "text artifact" is any artifact whose declared artifact type is `text`.

Text artifacts MUST be interpreted as UTF-8 and MUST undergo Unicode normalization and line-ending normalization.

Artifact type classification MUST NOT be inferred by file extension or by content sniffing.

Artifact types MUST be declared by the upstream manifest or protocol contract (see `spec/core/PROTOCOL_MANIFEST.md`).

### 3.6 Binary Artifact

A "binary artifact" is any artifact whose declared artifact type is `binary`.

Binary artifacts MUST be treated as raw bytes.

Binary artifacts MUST NOT undergo Unicode normalization, newline normalization, or any text decoding step.

---

## 4. Global Canonicalization Pipeline

Receivers MUST canonicalize artifacts using the following mandatory pipeline.

No step MAY be skipped.

Pipeline:

1. Byte ingestion
2. BOM handling
3. Artifact-type classification (`text` or `binary`)
4. Line ending normalization (text only)
5. Unicode normalization (text only)
6. Artifact-type specific normalization
7. Canonical byte emission

If canonicalization cannot complete deterministically, receiver MUST REJECT.

---

## 5. Encoding Rules (Text Artifacts)

### 5.1 UTF-8 Requirement

All text artifacts MUST be interpreted as UTF-8.

If a text artifact is not valid UTF-8, receiver MUST REJECT.

### 5.2 Byte Order Mark (BOM)

If a UTF-8 BOM is present, it MUST be removed.

If UTF-16 or UTF-32 BOM markers are detected (including but not limited to):

- `0xFF 0xFE`
- `0xFE 0xFF`
- `0x00 0x00 0xFE 0xFF`
- `0xFF 0xFE 0x00 0x00`

receiver MUST REJECT.

### 5.3 Null Bytes

Text artifacts MUST NOT contain null bytes (`0x00`).

If null bytes exist, receiver MUST REJECT.

---

## 6. Line Ending Normalization (Text Artifacts)

### 6.1 Canonical Line Ending

All text artifacts MUST normalize line endings to LF (`\n`, byte `0x0A`).

The following conversions MUST be applied:

- CRLF (`\r\n`) MUST be converted to LF (`\n`)
- CR (`\r`) MUST be converted to LF (`\n`)

### 6.2 Final Newline Rule

Text artifacts MUST end with exactly one LF.

Rules:

- If a file ends with no newline, receiver MUST append one LF.
- If a file ends with multiple trailing LF characters, receiver MUST reduce them to exactly one LF.

This rule normalizes only the end-of-file newline run; it MUST NOT remove any non-newline content.

---

## 7. Whitespace Normalization

### 7.1 Trailing Whitespace

For text artifacts, trailing whitespace at the end of a line MUST be preserved.

Whitespace trimming MUST NOT be applied unless explicitly stated by a downstream spec.

Receivers MUST NOT trim ASCII spaces (`0x20`) or tabs (`0x09`) at line end.

### 7.2 Tab Characters

Tab characters MUST be preserved exactly.

Tab expansion MUST NOT be performed.

---

## 8. Unicode Normalization (Text Artifacts)

### 8.1 Unicode Normalization Form

All text artifacts MUST be normalized to Unicode NFC.

NFC normalization MUST be applied to decoded Unicode scalar values, then re-encoded as UTF-8.

If a receiver cannot perform NFC normalization deterministically, receiver MUST REJECT.

NFC normalization is a canonical transformation and is considered part of artifact identity for all text artifacts.

### 8.2 Forbidden Transformations

Receivers MUST NOT perform:

- case folding
- locale-based conversions
- punctuation normalization
- emoji substitution
- smart quote substitution
- normalization other than NFC

---

## 9. Artifact-Type Specific Rules

### 9.1 Markdown Artifacts

Markdown artifacts MUST be treated as raw UTF-8 text artifacts.

Canonical bytes for markdown MUST be computed AFTER:

- BOM removal
- LF normalization
- NFC normalization

Markdown parsing MUST NOT affect canonical bytes.

Hashing is based on canonical bytes, not parsed AST.

### 9.2 YAML Frontmatter

If a markdown artifact contains YAML frontmatter:

- YAML frontmatter MUST be included in canonical bytes exactly as written
- YAML MUST NOT be reordered or re-emitted
- YAML formatting MUST NOT be modified
- Frontmatter is treated as part of the artifact

YAML frontmatter MUST be validated for admissibility before downstream acceptance.

Validation rules:

- YAML MUST be parseable as YAML 1.2
- duplicate keys MUST cause REJECT
- YAML tags (custom types) MUST cause REJECT
- anchors and aliases MUST cause REJECT

This validity check MUST NOT rewrite or re-emit YAML bytes.

Frontmatter bytes remain included in canonical bytes exactly as written, but invalid YAML is not admissible.

### 9.3 JSON Artifacts (Raw Text Mode)

If an artifact is a `.json` file, it MUST be treated as a raw text artifact for canonical bytes.

Receivers MUST NOT re-serialize `.json` artifact files unless explicitly required by another spec.

This prevents drift due to JSON serializer differences.

Receivers MUST NOT derive structured canonical JSON objects by parsing arbitrary `.json` artifact files for hashing purposes, unless an upstream spec section explicitly requires that specific artifact to be parsed and re-encoded via RFC 8785.

Absent an explicit upstream requirement, `.json` artifacts MUST be hashed from canonical bytes only.

### 9.4 Canonical JSON Objects (RFC 8785 Mode)

When a spec requires hashing a structured JSON object (such as VHI, manifest objects, or dependency snapshots):

- the object MUST be canonicalized using RFC 8785
- the resulting canonical JSON bytes MUST be used for hashing
- encoding MUST be UTF-8
- no extra whitespace is allowed

This rule applies ONLY to structured stable objects explicitly defined by specs.

It MUST NOT be applied to arbitrary `.json` artifact files unless explicitly mandated.

---

## 10. Canonical JSON Rules (RFC 8785)

### 10.1 Object Key Ordering

Object keys MUST be sorted lexicographically by Unicode code point order.

### 10.2 Array Ordering

Array order MUST be preserved exactly as defined by the input object.

If a spec defines an array as "order-insensitive", the receiver MUST sort it as required by that spec BEFORE canonical JSON encoding.

### 10.3 String Encoding

Strings MUST be encoded as UTF-8.

Unicode escapes MUST follow RFC 8785 canonical escaping rules.

### 10.4 Number Encoding

Numbers MUST be encoded according to RFC 8785.

Receivers MUST NOT emit `1.0` if `1` is canonical.

If a receiver cannot represent a number deterministically, receiver MUST REJECT.

Number encoding MUST follow RFC 8785 exactly.

### 10.5 Forbidden JSON Features

Receivers MUST reject JSON containing:

- NaN
- Infinity
- -Infinity

---

## 11. Canonical Hash Format

### 11.1 Hash Algorithm

All canonical hashes MUST use SHA-256.

No other algorithm is permitted.

### 11.2 Output Encoding

All hashes MUST be expressed as:

`sha256:<64 lowercase hex>`

Uppercase hex MUST NOT be used.

Missing prefix MUST NOT be allowed.

### 11.3 Hash Input

Hash input MUST be:

- canonical bytes for artifacts
- RFC 8785 canonical JSON bytes for structured objects

Hash input MUST NOT include:

- file path
- filename
- timestamps
- OS metadata
- filesystem permissions
- user identity metadata

---

## 12. Canonical Path Rules (Manifest / Registry Context)

### 12.1 Canonical Path Separator

Artifact paths MUST use forward slash `/`.

Backslash `\` MUST NOT be used.

### 12.2 No Relative Segments

Canonical paths MUST NOT contain:

- `./`
- `../`

If present, receiver MUST REJECT.

### 12.3 No Trailing Slash

Canonical file paths MUST NOT end with `/`.

### 12.4 Path Scope Rule

Path canonicalization rules apply only to:

- manifest references
- registry entries
- dependency snapshot keys

They do NOT apply to the content bytes of artifacts.

---

## 13. Compression / Archive Handling

### 13.1 No Implicit Decompression

Receivers MUST NOT decompress artifacts unless explicitly required by a downstream spec.

### 13.2 If Decompression is Required

If a downstream spec requires decompression, the decompression algorithm and ordering MUST be explicitly defined in that spec.

If undefined, receiver MUST REJECT.

---

## 14. Deterministic Failure Handling

If canonicalization cannot be completed deterministically, receiver MUST REJECT.

Canonicalization failure MUST NOT produce QUARANTINE.

This is because canonical bytes are a prerequisite for any deterministic governance evaluation.

---

## 15. Compliance Requirements

A receiver is compliant with this spec only if it:

- classifies artifacts deterministically using declared artifact types
- normalizes LF line endings deterministically for text artifacts
- enforces UTF-8 decoding for text artifacts
- applies NFC normalization for text artifacts
- uses RFC 8785 for structured stable JSON objects
- uses SHA-256 for all canonical hashes
- outputs hashes as `sha256:<64 lowercase hex>`
- rejects ambiguous or environment-dependent encodings

Any deviation MUST be treated as a governance violation.

---

## 16. Final Rule

Any ambiguity not explicitly resolved by this document MUST be treated as a failure condition.

Canonicalization MUST always prefer REJECT over "best effort".

This prevents silent drift and preserves frozen genome integrity.