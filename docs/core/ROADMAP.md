# ICS Core DNA — ROADMAP (Single Source Plan)

This document is the canonical step-by-step plan for building and freezing the ICS Core DNA.

Legend:
- ✅ Done
- 📍 Current focus
- ⬜ Planned

Rule:
If it is not in this roadmap, it does not exist.

---

## Phase 0 — Repo Discipline (Foundation)

### 0.1 Single Entry Point
- ✅ Create `docs/core/INDEX.md`

Acceptance Criteria:
- A newcomer can find the core docs in <60 seconds.
- INDEX explicitly states it is scaffolding.

---

## Phase 1 — "First Verdict" Pipeline (Minimum Court Exists)

### 1.1 Golden Vector Runner
- ✅ `tools/verify_vectors.py` exists and runs
- ✅ `expected.json` supports prefix error matching
- ✅ `make verify-vectors` passes

Acceptance Criteria:
- At least 1 valid vector must PASS.
- At least 3 invalid vectors must FAIL with expected error prefixes.
- Output is deterministic.

---

## Phase 2 — Verdict Contract (External Judgment Spec)

### 2.1 Verdict Spec v1
- 📍 ⬜ Write `docs/core/VERDICT_SPEC.md`

Purpose:
The verdict is the only output the outside world trusts.

Acceptance Criteria:
- Verdict is fully deterministic (byte-for-byte).
- No ambient inputs (time/env/platform) affect verdict.
- Defines PASS/FAIL/ERROR states.
- Defines canonical verdict bytes and verdict hash/digest.
- Defines required fields and optional fields.
- Defines stable error code embedding rules.

Failure Modes:
- Missing verdict fields
- Unknown verdict version
- Non-canonical verdict encoding

---

## Phase 3 — EvidenceBlob Contract (Input Spec)

### 3.1 EvidenceBlob Spec v1
- ⬜ Write `docs/core/EVIDENCEBLOB_SPEC.md`

Acceptance Criteria:
- EvidenceBlob is a strict container format.
- EvidenceBlob supports hash chaining.
- Null vs absent is explicitly defined.
- Unknown fields behavior is explicitly defined.
- Byte layout rules are explicit.

Failure Modes:
- Broken hash chain
- Missing mandatory evidence
- Unsupported version

---

## Phase 4 — Canonicalization Rules (No Drift Allowed)

### 4.1 Canonicalization Spec v1
- ⬜ Write `docs/core/CANONICALIZATION.md`

Acceptance Criteria:
- Map ordering rules explicit.
- Duplicate key handling explicit.
- Unicode normalization policy explicit.
- Newline / whitespace policy explicit.
- Numeric canonicalization policy explicit (or explicitly forbidden).

Failure Modes:
- Non-canonical encoding
- Duplicate keys
- Platform-dependent normalization

---

## Phase 5 — Error Code Constitution

### 5.1 Error Codes v1
- ⬜ Write `docs/core/ERROR_CODES.md` (formalize)

Acceptance Criteria:
- Error namespaces (PARSE/CANON/VERIFY/RULES/VERDICT) are defined.
- Prefix stability is guaranteed.
- Each error has deterministic reproduction conditions.

---

## Phase 6 — Judge (Core) Module Boundaries

### 6.1 Core Modules
- ⬜ Lock core module boundaries

Target structure:
- `ics_core::parse`
- `ics_core::canon`
- `ics_core::verify`
- `ics_core::rules`
- `ics_core::verdict`

Acceptance Criteria:
- Each module has explicit responsibility.
- Each module defines its own failure modes.
- No cross-layer leakage.

---

## Phase 7 — Stress Test Suite (Attack the DNA)

### 7.1 Determinism Stress
- ⬜ Replay tests (same input N times)
- ⬜ Concurrency tests (multi-thread)
- ⬜ Cross-platform drift detection (future CI)

Acceptance Criteria:
- Same EvidenceBlob always produces identical Verdict bytes.

---

### 7.2 Canonicalization Stress
- ⬜ null vs absent test vectors
- ⬜ duplicate keys vectors
- ⬜ unicode normalization vectors
- ⬜ map ordering vectors

Acceptance Criteria:
- All non-canonical inputs must fail deterministically.

---

## Phase 8 — CI/CD Enforcement

### 8.1 CI Pipeline
- ⬜ Add GitHub Actions workflow

Required jobs:
- fmt
- clippy
- test
- verify-vectors
- minimal stress suite

Acceptance Criteria:
- Any nondeterminism becomes a CI failure.

---

## Phase 9 — Core Freeze v1 (DNA Lock)

### 9.1 Freeze Criteria Document
- ⬜ Write `docs/core/CORE_FREEZE.md`

Acceptance Criteria:
- Verdict spec locked.
- EvidenceBlob spec locked.
- Canonicalization locked.
- Error codes locked.
- Golden vectors locked.
- CI determinism suite green.

Output:
- Tag: `core/v1.0.0-freeze`

---

## Phase 10 — Sector Layer Begins (First Adapter)

### 10.1 First Sector Adapter (Game/UE5)
- ⬜ Add `integrations/ue5/` (or sector adapter folder)

Acceptance Criteria:
- Sector adapter never modifies Core DNA.
- Sector adapter only produces EvidenceBlob.
- Core remains offline-verifiable.

---

## Notes

Core Philosophy:
- Tentacles explore, Genome decides.
- No policy injection into the Genome.
- Canonical bytes are sacred.
