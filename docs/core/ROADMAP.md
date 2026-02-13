
# ISC-CORE ROADMAP (PROCESS CONTRACT)

This file is a **process contract**, not a protocol specification.
It defines the required workflow, document lifecycle states, and enforcement rules.

This roadmap is **normative for repository process**.

---

## 0. Definitions

### 0.1 Document
A "document" means any `.md` file under `docs/` or `spec/` that defines requirements,
formats, algorithms, invariants, or validation rules.

### 0.2 Normative Keywords
The following keywords are normative and must be interpreted as in RFC-style usage:

- MUST
- MUST NOT
- REQUIRED
- SHALL
- SHALL NOT
- SHOULD
- SHOULD NOT
- MAY

### 0.3 Document State
Every document MUST be in exactly one state:

- DRAFT
- HARDENED
- FROZEN

State MUST be declared inside the document itself (machine-readable).

### 0.4 Upstream / Downstream
This roadmap defines a strict order of documents.

- Upstream(D) = all documents listed earlier than D in Section 1.
- Downstream(D) = all documents listed later than D in Section 1.

This ordering is the **only canonical upstream definition**.

---

## 1. Canonical Roadmap Order (Upstream Chain)

This list is the single source of truth for dependency ordering.

1. `docs/core/INDEX.md`
2. `docs/core/ROADMAP.md`
3. `spec/core/STATE_MACHINE.md`
4. `spec/core/SEQUENTIAL_LOCK_RULE.md`
5. `spec/core/FREEZE_POLICY.md`
6. `spec/core/VERSIONING_PATH.md`
7. `spec/core/CI_ENFORCEMENT_HOOKS.md`

If a new document is added, it MUST be inserted into this list.
Insertion expands upstream requirements automatically.

---

## 2. State Machine

### 2.1 Allowed Transitions
State transitions are one-way only:

- DRAFT -> HARDENED
- HARDENED -> FROZEN

The following transitions are forbidden:

- HARDENED -> DRAFT
- FROZEN -> HARDENED
- FROZEN -> DRAFT

State regression MUST NOT occur.

### 2.2 State Must Be Declared in Document Frontmatter
Every document MUST begin with YAML frontmatter (real frontmatter, not a YAML snippet).

Example frontmatter (this is what must appear at the very top of each document):

```md
---
state: DRAFT
version: v1
---
Required fields:
state: one of DRAFT|HARDENED|FROZEN
version: semantic identifier such as v1, v2
Optional fields:
upstreams: list of explicit upstream paths (for audit only)
last_hardened_commit: git SHA (audit only)
Rules:
If state is absent, CI MUST fail.
If version is absent, CI MUST fail.
If state is unknown, CI MUST fail.
If multiple state declarations exist, CI MUST fail.
This avoids silent drift and prevents null/absent ambiguity.
3. Sequential Lock Rule (Hard Gate)
3.1 Hard Rule
A document MUST NOT advance beyond the state of any of its upstream documents.
Formally:
For any document D:
If any U in upstream(D) is DRAFT, then D MUST NOT be HARDENED or FROZEN.
If any U in upstream(D) is HARDENED, then D MUST NOT be FROZEN.
This is a strict sequential lock.
3.2 Practical Meaning
If an upstream document is not stabilized, downstream specs must remain incomplete by design. This prevents premature freezing of dependent specs.
4. HARDENED Requirements
A document MAY be promoted to HARDENED only if all requirements below are satisfied.
4.1 Normative Completeness
The document MUST NOT contain open-ended placeholders such as:
TODO
TBD
???
"later"
"to be decided"
"we will define"
"maybe"
Exception: These markers are allowed inside fenced code blocks only.
CI MUST treat these markers as forbidden in prose.
4.2 Determinism
If the document defines parsing, serialization, canonicalization, hashing, signing, or validation rules, then it MUST define deterministic behavior.
The following MUST be explicitly specified:
byte ordering rules
field ordering rules
canonical encoding format
whitespace normalization rules (if relevant)
case sensitivity rules
numeric encoding rules
string encoding rules (UTF-8 etc.)
4.3 Null vs Absent
If the document defines data formats, it MUST explicitly define:
what "null" means (if allowed)
what "absent/missing field" means
whether null and absent are equivalent or distinct
whether unknown fields are ignored, rejected, or preserved
Silent ambiguity is forbidden