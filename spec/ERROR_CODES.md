---
state: DRAFT
version: v1.1
---

# ISC-CORE ERROR CODES SPEC

This document defines the canonical error / warning / quarantine code contract for ISC Core.

It specifies:

- the canonical namespaces (E / Q / W)
- deterministic precedence rules
- stability guarantees (no rename, no semantic drift)
- minimum required code set
- how codes affect verdict decisions and stable hashing

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/VERDICT_SPEC.md
- spec/CANONICALIZATION.md
- spec/EVIDENCE_BLOB.md
- spec/core/PROTOCOL_MANIFEST.md

---

## 1. Purpose

ISC Core is treated as a frozen genome.

Therefore:

- all reason codes MUST be deterministic identifiers
- codes MUST be stable across time and receivers
- ambiguous interpretation MUST be treated as a failure condition
- code meaning MUST NOT drift silently
- codes MUST allow deterministic verdict derivation

This document defines the only allowed canonical reason code system.

---

## 2. Scope

This specification governs:

- reason code namespaces
- code formatting rules
- code precedence and verdict dominance rules
- required minimal code list
- compatibility and versioning rules

This specification does NOT define:

- human-readable message formats
- UI rendering rules
- receiver logging formats
- stack traces or debug output fields

---

## 3. Definitions

### 3.1 Reason Code

A reason code is a stable string identifier emitted by a receiver.

A reason code MUST be machine-readable and deterministic.

A reason code MUST be stable across receivers.

### 3.2 Reason Object

A reason object is an optional structured diagnostic object that MAY include:

- code
- message
- path
- details

Only code is stable.

All other fields are audit-only.

### 3.3 Code Namespace

A code namespace is the leading letter prefix that defines the class of a code:

- E = Error (REJECT class)
- Q = Quarantine trigger (QUARANTINE class)
- W = Warning (ACCEPT class)

---

## 4. Canonical Code Format

All reason codes MUST follow one of the following formats:

- `E<3 digits>`
- `Q<3 digits>`
- `W<3 digits>`

Examples:

- E201
- Q120
- W001

Lowercase prefixes are forbidden.

If a receiver emits a malformed code, receiver MUST REJECT with E001.

---

## 5. Code Semantics by Namespace

### 5.1 E*** (Error)

E*** codes represent deterministic fatal violations.

If any E*** code exists in normalized reason_codes:

- final verdict MUST be REJECT

### 5.2 Q*** (Quarantine)

Q*** codes represent deterministic incomplete evaluation conditions.

If at least one Q*** code exists and no E*** code exists:

- final verdict MUST be QUARANTINE

Q*** MUST only be used for conditions explicitly allowed by VERDICT_SPEC.

### 5.3 W*** (Warning)

W*** codes represent non-fatal diagnostic signals.

Warnings MUST NOT prevent ACCEPT.

If only W*** codes exist:

- final verdict MUST be ACCEPT

---

## 6. Precedence Rules

Receivers MUST apply the following dominance rule:

REJECT dominates QUARANTINE dominates ACCEPT.

Therefore:

- If any E*** exists => REJECT
- Else if any Q*** exists => QUARANTINE
- Else => ACCEPT (with optional warnings)

Receivers MUST NOT override this precedence.

---

## 7. reason_codes Normalization Rules

### 7.1 Stable Set

reason_codes MUST be normalized as follows:

- codes MUST be treated as a set
- duplicates MUST be removed
- the final set MUST be sorted lexicographically

Duplicate presence MUST NOT change the final normalized reason_codes set.

### 7.2 Ordering

The output reason_codes array MUST be sorted lexicographically.

Example ordering:

- E101
- E201
- Q120
- Q150
- W001

Receivers MUST NOT preserve original emission order.

---

## 8. Stable vs Audit Fields

Only reason_codes MUST affect stable verdict hashing.

Any of the following MUST be treated as audit-only:

- reason message strings
- file paths
- section pointers
- stack traces
- exception names
- receiver-local debug details

If any audit-only content affects verdict_hash, receiver is non-compliant.

---

## 9. Reserved Code Ranges

To prevent semantic collision, the following ranges are reserved.

### 9.1 E000–E099 (Meta / Receiver Compliance)

Reserved for receiver-level violations.

These codes indicate the receiver cannot comply deterministically.

### 9.2 E100–E199 (Canonicalization / Parsing)

Reserved for DOC_FORMAT and CANONICALIZATION failures.

### 9.3 E200–E299 (Dependency / Locking)

Reserved for dependency resolution, cycle detection, and state locking.

### 9.4 E300–E399 (Evidence Failures)

Reserved for evidence manifest and evidence integrity failures.

### 9.5 E400–E499 (Verdict Output Contract)

Reserved for stable hashing / output schema violations.

### 9.6 Q100–Q199 (Canonical QUARANTINE Triggers)

Reserved for the closed-set QUARANTINE trigger codes defined by VERDICT_SPEC.

### 9.7 W000–W099 (Non-Fatal Governance Warnings)

Reserved for warning-level signals.

---

## 10. Minimal Required Canonical Codes

A compliant receiver MUST support the following minimal code set.

### 10.1 Meta / Receiver Compliance

- E000: UNKNOWN_REASON_CODE
- E001: MALFORMED_REASON_CODE
- E010: NON_DETERMINISTIC_EVALUATION_DETECTED

### 10.2 Canonicalization / Parsing Errors

- E110: INVALID_UTF8
- E111: NULL_BYTE_IN_TEXT
- E120: CANONICALIZATION_FAILED
- E130: PATH_NOT_CANONICAL
- E140: YAML_FRONTMATTER_INVALID
- E150: MARKDOWN_PARSE_FAILED

### 10.3 Metadata / Manifest Errors

- E160: METADATA_MISSING_REQUIRED_FIELD
- E161: METADATA_LOCATION_INVALID
- E170: ARTIFACT_TYPE_MISSING
- E171: ARTIFACT_TYPE_UNKNOWN

### 10.4 Dependency Errors

- E200: DEPENDENCY_DECLARATION_MISSING
- E201: DEPENDENCY_VERSION_UNRESOLVABLE
- E202: DEPENDENCY_AMBIGUOUS_VERSION
- E210: DEPENDENCY_CYCLE_DETECTED
- E220: STATE_LOCK_RULE_VIOLATION

### 10.5 Evidence Errors

- E300: EVIDENCE_MANIFEST_MALFORMED
- E301: EVIDENCE_ID_INVALID_FORMAT
- E302: EVIDENCE_HASH_MISMATCH
- E303: EVIDENCE_SIZE_MISMATCH
- E310: DUPLICATE_EVIDENCE_ID

### 10.6 Verdict Output Errors

- E400: VERDICT_OUTPUT_NOT_JSON
- E410: VERDICT_HASH_INVALID
- E420: VERDICT_HASH_INPUT_INVALID
- E430: RULESET_ID_INVALID_FORMAT

### 10.7 Quarantine Trigger Codes (Closed Set)

These MUST match VERDICT_SPEC.

- Q100: TIME_SOURCE_MISSING_FOR_TIME_SENSITIVE
- Q110: TIME_SOURCE_UNVERIFIABLE
- Q120: DEPENDENCY_RESOLUTION_INCOMPLETE
- Q130: REORDER_OUT_OF_ORDER
- Q140: RECEIVER_RESOURCE_LIMIT_EXPLICIT
- Q150: METADATA_LOCATION_INVALID
- Q160: CANONICAL_PARSE_UNSAFE_BUT_RECOVERABLE

### 10.8 Warning Codes

- W001: NON_FATAL_SCHEMA_DEVIATION
- W010: UNUSED_METADATA_FIELD_PRESENT
- W020: OPTIONAL_FIELD_MISSING

---

## 11. Code Emission Rules

### 11.1 Mandatory Code Requirement

If a receiver produces REJECT, it MUST emit at least one E*** code.

If a receiver produces QUARANTINE, it MUST emit at least one Q*** code.

If a receiver produces ACCEPT with warnings, it MUST emit at least one W*** code.

If a receiver produces ACCEPT with no warnings, reason_codes MAY be empty.

### 11.2 Namespace Consistency

Receivers MUST ensure:

- REJECT verdict MUST NOT be emitted without E*** codes
- QUARANTINE verdict MUST NOT be emitted without Q*** codes
- ACCEPT verdict MUST NOT include any E*** or Q*** codes

If inconsistency is detected, receiver MUST REJECT with E010.

---

## 12. Stable Meaning and No-Rename Rule

Reason code meanings MUST NOT be changed silently.

Once introduced:

- codes MUST NOT be renamed
- codes MUST NOT be reassigned to a different meaning
- codes MUST NOT change namespace class

If semantic meaning must change:

- a new code MUST be introduced
- the old code MUST remain reserved
- ruleset_id MUST change

---

## 13. Backward Compatibility

Frozen code meanings MUST remain valid forever.

Receivers MUST continue to recognize previously frozen codes.

Unknown codes MUST be treated as a fatal error unless explicitly permitted by a downstream version bump.

If a receiver encounters an unknown code:

- receiver MUST REJECT with E000

---

## 14. Deterministic Mapping Requirement

Given identical evaluation inputs, compliant receivers MUST produce identical:

- verdict
- reason_codes set
- reason_codes ordering

If two receivers disagree on code emission, determinism is violated.

---

## 15. Compliance Requirements

A receiver is compliant with this specification only if it:

- enforces canonical code format
- enforces deterministic sorting of reason_codes
- enforces namespace dominance rules
- never allows audit-only data to influence stable hashing
- supports the minimal required code set

Any deviation MUST be treated as a governance violation.

---

## 16. Final Rule

Any ambiguity in reason code meaning MUST be treated as a failure condition.

In DRAFT state, receivers MAY QUARANTINE.

In HARDENED and FROZEN state, ambiguity MUST produce REJECT.