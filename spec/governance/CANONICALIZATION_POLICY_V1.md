# Canonicalization Policy v1

This document defines normative numeric edge-case behavior for ISC Core v1.

## Negative Zero

- Inputs containing negative zero forms (e.g., -0, -0.0) MUST be accepted if valid JSON.
- Canonical output MUST normalize negative zero to 0.
- Canonical output MUST NOT contain -0 or -0.0 representations.

Rationale:
Most JSON parsers normalize -0 to 0 during parsing.
v1 aligns with cross-platform deterministic behavior and avoids raw-text scanning complexity.


## Scientific Notation

- Scientific notation forms (e.g., 1e3, 1E+3) MUST be rejected in v1.

