# ISC Core Limits v1 (Normative)

This document defines the mandatory input limits for ISC Core.

## MAX_DEPTH

Implementations MUST reject any input whose nesting depth exceeds:

MAX_DEPTH = 64

Depth is counted as:
- Object increases depth by 1 when entering its value context
- Array increases depth by 1 when entering its element context

On violation, implementations MUST emit:
DEPTH_LIMIT_EXCEEDED

## MAX_INPUT_BYTES

Implementations MUST reject any input whose raw UTF-8 encoded JSON byte length exceeds:

MAX_INPUT_BYTES = 65536

This limit applies to the raw JSON text prior to parsing/canonicalization.

On violation, implementations MUST emit:
SIZE_LIMIT_EXCEEDED

## Versioning

Any change to these limits MUST require a MAJOR version bump.

