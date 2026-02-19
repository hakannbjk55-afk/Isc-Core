# ISC Core Constitution

This document defines the non-negotiable principles of the ISC core.
Changes to any MUST/SHALL rule in this document REQUIRE a MAJOR version bump.

## 1. Deterministic Canonical Output (MUST)
- The same logical input MUST yield the same canonical byte sequence.
- Canonicalization MUST be platform-independent (OS / runtime / locale MUST NOT change output).
- Idempotence MUST hold: canon(canon(x)) == canon(x).
- Any change that alters canonical bytes for any valid input REQUIRES a MAJOR version bump.

## 2. Strict Structural Parsing (MUST)
- Parsing MUST be strict and unambiguous.
- Duplicate object keys MUST be rejected (HARD FAIL).
- Inputs that rely on permissive parsing MUST be rejected.
- Any relaxation or ambiguity introduced here REQUIRES a MAJOR version bump.

## 3. Byte-Level Authority and Non-Interpretation (MUST)
- The core MUST treat inputs as opaque data for the purpose of sealing.
- The core MUST NOT apply implicit semantic transformations, including but not limited to:
  Unicode normalization, line-ending normalization, locale transforms, or "helpful" rewriting.
- If normalization or semantic transformation is desired, it SHALL be performed explicitly
  before evidence capture. The resulting bytes are what the core seals.
- The core "seals what it sees" and MUST NOT attempt to infer intent or meaning.

## 4. Golden Governance (MUST)
- Canonical behavior is defined by the pinned corpus (test vectors) and golden hashes.
- A mismatch between produced canonical results and pinned golden values MUST fail CI.
- Updating golden values MUST be a deliberate, reviewed change (no automatic golden updates).

## 5. CI as Court (MUST)
- CI is the enforcement authority for determinism and pinned behavior.
- A change that breaks pinned behavior MUST NOT be merged without explicit governance action
  (vector update and/or golden update as appropriate).

## 6. Evidence Pack Determinism (MUST)
- Evidence bundles MUST be reproducible: same inputs -> same pack bytes -> same pack hash.
- File ordering MUST be deterministic (lexicographic by path).
- Archive metadata MUST be normalized (uid/gid, mtime, etc.) as specified by the pack format.

## 7. Version Governance (SHALL)
- Changes to any MUST/SHALL rule in this Constitution REQUIRE a MAJOR version bump.
- Adding new test vectors is permitted without MAJOR bump, provided it does not alter existing
  canonical bytes for previously-valid inputs.
- Refactoring implementation without changing canonical bytes does not require a MAJOR bump.
