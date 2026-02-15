---
state: DRAFT
version: v1
---

# ISC-CORE ERROR CODES SPEC

This document defines the canonical error and reason code taxonomy for ISC Core.

It specifies:

- how reason codes MUST be structured
- how code namespaces MUST map to verdict classes
- how deterministic reason_codes MUST be generated
- how errors MUST be classified to prevent receiver policy drift

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/core/DOC_FORMAT.md
- spec/VERDICT_SPEC.md

---

## 1. Purpose

ISC Core is treated as a frozen genome.

Therefore:

- error classification MUST be deterministic
- reason code emission MUST be reproducible
- code meanings MUST be stable across versions
- ambiguity MUST be treated as a failure condition

This spec exists to prevent:

- inconsistent verdict mappings
- "receiver-specific error policy"
- unstable reason_codes ordering
- non-canonical error naming drift

---

## 2. Definitions

### 2.1 Reason Code

A reason code is a short canonical identifier representing a specific evaluation outcome.

Reason codes MUST be stable and machine-consumable.

### 2.2 Namespace

A namespace is the leading prefix of a reason code.

Namespaces determine the required verdict class.

### 2.3 Reason Object

A reason object is an optional audit-only structured output.

Only reason code strings influence stable hashing.

---

## 3. Canonical Namespaces

Reason codes MUST use exactly one of the following namespaces:

- `E***` = REJECT (error / invalid)
- `Q***` = QUARANTINE (determinism incomplete)
- `W***` = ACCEPT (warning only)
- `I***` = informational (ACCEPT only, audit-only)

No other namespace is allowed.

If an unknown namespace is encountered, receiver MUST REJECT.

---

## 4. Namespace-to-Verdict Mapping (Hard Rule)

### 4.1 Mapping Table

The following mapping is mandatory:

- `E***` codes MUST imply verdict = REJECT
- `Q***` codes MUST imply verdict = QUARANTINE
- `W***` codes MUST imply verdict = ACCEPT
- `I***` codes MUST imply verdict = ACCEPT

### 4.2 Mixed Code Sets

Receivers MAY emit multiple codes.

When multiple codes exist, the final verdict MUST be the strongest class.

Strength order:

`REJECT > QUARANTINE > ACCEPT`

Examples:

- codes: `[W010, W020]` => ACCEPT
- codes: `[Q120, W010]` => QUARANTINE
- codes: `[E201, Q120]` => REJECT

Receivers MUST NOT output a verdict inconsistent with the strongest code class.

---

## 5. Canonical Code Format

### 5.1 Syntax

Reason codes MUST follow:

`<PREFIX><3 digits>`

Where:

- PREFIX is one of: `E`, `Q`, `W`, `I`
- digits MUST be decimal
- total length MUST be 4 characters

Examples:

- `E201`
- `Q130`
- `W010`

Invalid examples:

- `E20`
- `ERR201`
- `q130`
- `E201A`

If a code is malformed, receiver MUST REJECT.

### 5.2 Case Sensitivity

Codes MUST be uppercase.

Lowercase codes MUST be treated as invalid.

---

## 6. reason_codes Output Requirements

### 6.1 reason_codes Set

Receivers MUST emit:

- `reason_codes` as an array of strings

The array MUST contain only valid codes.

### 6.2 Ordering

`reason_codes` MUST be sorted lexicographically ascending.

### 6.3 Duplicate Handling

Duplicate codes MUST be removed during normalization.

Receivers MUST treat duplicates as a normalization operation, not as a verdict-changing event.

After normalization, duplicates MUST NOT remain.

### 6.4 Empty reason_codes

If verdict is ACCEPT, reason_codes MAY be empty.

If verdict is REJECT or QUARANTINE, reason_codes MUST NOT be empty.

---

## 7. Reason Objects (Audit-Only)

Receivers MAY emit audit-only reason objects.

If present, each reason object MUST contain:

- `code` (string)
- `message` (string)

Reason objects MAY contain:

- `path`
- `details`

Reason objects MUST NOT affect verdict_hash computation.

Receivers MUST NOT include reason objects in VHI hashing.

---

## 8. Canonical Code Registry

### 8.1 Rule

The set of valid codes MUST be treated as a closed registry.

Receivers MUST NOT invent new codes.

New codes may only be introduced by updating this document version.

### 8.2 Forward Compatibility

If a receiver encounters an unknown code from a newer ruleset:

- in DRAFT: receiver MAY QUARANTINE
- in HARDENED: receiver MUST QUARANTINE
- in FROZEN: receiver MUST REJECT

---

## 9. Canonical Error Codes

This section defines the mandatory reason codes and their canonical meaning.

---

## 10. E-Codes (REJECT)

### E100: ARTIFACT_TYPE_MISSING

artifact_type is missing or absent.

### E101: ARTIFACT_TYPE_INVALID

artifact_type is present but not a valid value.

### E110: METADATA_REQUIRED_FIELD_MISSING

A required metadata field is missing.

### E120: DEPENDENCY_DECLARATION_MISSING

Dependency declaration block is missing when required.

### E121: DEPENDENCY_VERSION_INVALID

Dependency version is malformed or invalid.

### E130: DEPENDENCY_CYCLE_DETECTED

A dependency cycle exists.

### E140: RULESET_ID_INVALID

ruleset_id is missing or not canonical.

### E150: CANONICAL_BYTES_INVALID

Canonical byte normalization failed deterministically.

### E160: CANONICAL_PARSE_FAILED

Parsing failed deterministically under canonical parser rules.

### E170: UNKNOWN_NAMESPACE

A reason code namespace is invalid or unknown.

### E180: OUTPUT_SCHEMA_INVALID

Receiver output is missing mandatory stable fields.

### E190: UNKNOWN_FAILURE_CLASSIFICATION

Receiver encountered an error but could not classify it.

This code MUST only be used if no other E-code applies.

### E200: TTL_EXPIRED

Artifact TTL expired under an approved time source.

### E210: VERSION_AMBIGUITY

Multiple versions satisfy a dependency, producing ambiguity.

### E220: MULTIPLE_METADATA_SOURCES

Artifact contains multiple competing metadata declarations.

### E230: NON_CANONICAL_FORMAT_VIOLATION

Artifact violates canonical formatting rules defined by DOC_FORMAT.

---

## 11. Q-Codes (QUARANTINE)

### Q100: TIME_SOURCE_MISSING_FOR_TIME_SENSITIVE

time_sensitive = true and ttl_seconds exists, but time_source_type is missing.

### Q110: TIME_SOURCE_UNVERIFIABLE

Time source is present but cannot be verified deterministically.

### Q120: DEPENDENCY_RESOLUTION_INCOMPLETE

Dependency snapshot cannot be resolved deterministically.

### Q130: REORDER_OUT_OF_ORDER

Artifact violates reorder constraints.

### Q140: RECEIVER_RESOURCE_LIMIT_EXPLICIT

Receiver explicitly hit a resource limit (memory, CPU, disk, timeout).

### Q150: METADATA_LOCATION_INVALID

Metadata exists but is not found at canonical location.

### Q160: CANONICAL_PARSE_UNSAFE_BUT_RECOVERABLE

Artifact parsing is unsafe or ambiguous but may be recoverable.

---

## 12. W-Codes (ACCEPT WITH WARNING)

### W010: OPTIONAL_FIELD_MISSING

Optional field missing (allowed under current maturity state).

### W020: LEGACY_FIELD_USED

Legacy field detected.

### W030: NON_FATAL_FORMAT_DEVIATION

Format deviation detected but permitted in DRAFT mode.

---

## 13. I-Codes (INFORMATIONAL)

### I001: RECEIVER_VERSION_TAG

Receiver emitted a version tag.

### I010: AUDIT_TRACE_AVAILABLE

Audit trace exists.

I-codes MUST NOT be included in stable reason_codes unless explicitly allowed by VERDICT_SPEC.

---

## 14. Canonical Trigger Mapping Rules

Receivers MUST map evaluation failures to reason codes deterministically.

### 14.1 Priority Rule

If multiple codes apply, receiver MUST include all relevant codes.

The strongest code class MUST dominate verdict.

### 14.2 Classification Rule

Receivers MUST NOT collapse errors into generic codes if a specific code exists.

Example:

- dependency cycle => MUST emit `E130`, not `E190`

### 14.3 Unknown Failure

If receiver cannot classify a failure:

- MUST emit `E190`
- MUST set verdict = REJECT

---

## 15. Compliance Requirements

A receiver is compliant only if it:

- emits only codes defined in this document
- enforces namespace verdict mapping
- sorts reason_codes lexicographically
- removes duplicates deterministically
- never allows audit-only reason objects to influence verdict_hash

Any deviation MUST be treated as a governance violation.

---

## 16. Final Rule

If a condition is not explicitly assigned to a code in this registry, the receiver MUST treat it as:

- QUARANTINE only if it matches a known Q-trigger
- otherwise REJECT (E190)