
# ISC-CORE INDEX (CANONICAL ENTRY POINT)

This file is a process contract, not a protocol specification.

This index is normative for repository structure, file roles, and document precedence.

---

## 1. Canonical Repository Layout

The repository MUST use the following top-level structure:

- `core/`  
  Implementation code. MUST remain deterministic.

- `docs/`  
  Process and repository governance documents.

- `spec/`  
  Protocol specifications and normative requirements.

- `vectors/`  
  Canonical test vectors and golden fixtures.

- `tools/`  
  CI enforcement scripts, generators, and verification utilities.

No other top-level directories are allowed, except:

- `.github/`

---

## 2. Directory Semantics

### 2.1 `docs/`

Contains repository process contracts.

Examples:
- lifecycle rules
- freezing policy
- sequential lock rule
- CI enforcement rules

### 2.2 `spec/`

Contains protocol and format specifications.

These documents define canonical behavior.

### 2.3 `core/`

Contains the implementation.

Implementation MUST follow `spec/` exactly.

### 2.4 `vectors/`

Contains golden vectors.

Vectors MUST NOT be silently modified or replaced.

### 2.5 `tools/`

Contains CI enforcement tools and validation scripts.

---

## 3. Document Precedence Order

When two documents conflict, the following precedence order MUST be applied:

1. `spec/` documents
2. `docs/core/ROADMAP.md`
3. `docs/` process contracts
4. `core/` implementation
5. `tools/` utilities
6. `README.md`

---

## 4. Canonical Entry Point

The canonical entry point for repository governance is:

- `docs/core/INDEX.md` (this file)
- `docs/core/ROADMAP.md`

---

## 5. Required Core Documents

The following documents MUST exist:

- `docs/core/INDEX.md`
- `docs/core/ROADMAP.md`

---

## 6. Document State Requirement

All `.md` documents under `docs/` and `spec/` MUST begin with YAML frontmatter.

Example:

```md
---
state: DRAFT
version: v1
---
Required fields:
state: one of DRAFT|HARDENED|FROZEN
version: semantic identifier such as v1, v2
State MUST NOT be absent.
State regression MUST NOT occur.
7. Naming Conventions
All normative documents MUST be named in uppercase.
Examples:
STATE_MACHINE.md
FREEZE_POLICY.md
SEQUENTIAL_LOCK_RULE.md
8. ROADMAP Consistency Requirement
The document ordering defined in docs/core/ROADMAP.md MUST be consistent with this INDEX.
If the ordering diverges, CI MUST fail.
9. Determinism Constraint
The core/ implementation MUST be deterministic.
It MUST NOT depend on:
system time
randomness
network calls
environment-dependent behavior
All such behavior MUST be isolated to tools/ only.
10. Vector Immutability Contract
Golden vectors MUST NOT be replaced without explicit versioning.
Future enforcement SHOULD require:
a vectors/index.json manifest
hashes for all vector files
CI verification of hashes
11. Final Rule
This repository MUST remain machine-enforceable.
