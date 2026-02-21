# ISC Core Error Registry v1

This document defines the normative error codes for ISC Core.
All error codes are stable identifiers and MUST NOT be changed without a MAJOR version bump.

## Principles

- Implementations MUST emit the same error code for the same invalid input class.
- Error messages (human text) MAY differ, but the error code MUST match.
- If multiple errors could apply, the implementation MUST select the first applicable error by the precedence rules defined here.

## Error Code Format

Error codes MUST be uppercase identifiers with underscores, e.g.:
DUPLICATE_KEY

## Precedence Rule (Deterministic Failure)

When validating/parsing/canonicalizing, errors MUST be selected in this order:

1) INVALID_UTF8
2) INVALID_UTF8_SURROGATE
3) DUPLICATE_KEY
4) SCIENTIFIC_NOTATION
5) NEGATIVE_ZERO_POLICY
6) NAN_INFINITY
7) INTEGER_RANGE
8) DEPTH_LIMIT_EXCEEDED
9) SIZE_LIMIT_EXCEEDED
10) OTHER_INVALID_INPUT

## Registry

### INVALID_UTF8
Trigger: Input contains invalid UTF-8 byte sequences.
Requirement: MUST reject.

### INVALID_UTF8_SURROGATE
Trigger: Input contains lone surrogate code points (e.g., "\\ud800").
Requirement: MUST reject.

### DUPLICATE_KEY
Trigger: Any JSON object contains duplicate keys.
Requirement: MUST reject.

### SCIENTIFIC_NOTATION
Trigger: Any numeric token uses exponent form (e/E), e.g. 1e3.
Requirement: MUST reject.

### NEGATIVE_ZERO_POLICY
Trigger: Negative zero occurs as an input numeric value.
Requirement: v1 policy MUST normalize -0 to 0 in canonical output.

### NAN_INFINITY
Trigger: NaN, Infinity, -Infinity occurs as numeric input.
Requirement: MUST reject.

### INTEGER_RANGE
Trigger: Integer exceeds the accepted numeric range defined by the canonical profile.
Requirement: MUST reject.

### DEPTH_LIMIT_EXCEEDED
Trigger: Input exceeds maximum nesting depth (if limits are enabled).
Requirement: MUST reject.

### SIZE_LIMIT_EXCEEDED
Trigger: Input exceeds maximum accepted size (if limits are enabled).
Requirement: MUST reject.

### OTHER_INVALID_INPUT
Trigger: Any other invalid input not classified above.
Requirement: MUST reject.

