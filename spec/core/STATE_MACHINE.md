
---
state: DRAFT
version: v1
---

# ISC-CORE STATE MACHINE

This document defines the canonical lifecycle state machine for all normative documents in this repository.

This is a protocol governance contract, not an implementation guide.

---

## 1. Scope

This state machine applies to all `.md` documents under:

- `docs/`
- `spec/`

It does NOT apply to:

- source code files under `core/`
- tooling scripts under `tools/`
- binary artifacts

---

## 2. States

Each document MUST be in exactly one of the following states:

- `DRAFT`
- `HARDENED`
- `FROZEN`

A document MUST declare its state at the top using a YAML header.

Example:

```yaml
---
state: DRAFT
version: v1
---
3. State Definitions
3.1 DRAFT
A document in DRAFT state:
MAY contain TODO items
MAY contain unresolved ambiguity
MAY change structure, requirements, and terminology
MUST NOT be considered stable
DRAFT is the only state where large structural edits are allowed.
3.2 HARDENED
A document in HARDENED state:
MUST have no TODO sections
MUST have no placeholder text
MUST have complete definitions
MUST have complete invariants and validation rules
MUST be implementable by an external party
A HARDENED document is considered stable but not yet immutable.
Semantic changes are allowed but MUST be justified and versioned.
3.3 FROZEN
A document in FROZEN state is immutable.
A FROZEN document:
MUST NOT change its normative requirements
MUST NOT change any encoding rules
MUST NOT change canonicalization rules
MUST NOT change validation outcomes
MUST NOT change error behavior
A FROZEN document may only receive:
formatting changes
typo fixes that do not change meaning
clarifications that do not alter requirements
Semantic changes require:
a new version (v2, v3, ...)
new vectors
migration notes
4. Allowed Transitions
The allowed state transitions are:
DRAFT → HARDENED
HARDENED → FROZEN
A document MUST NOT transition backward.
Invalid transitions:
HARDENED → DRAFT
FROZEN → HARDENED
FROZEN → DRAFT
5. Promotion Rules
5.1 DRAFT → HARDENED
A document MAY be promoted to HARDENED only if:
all sections are complete
all invariants are defined
all MUST / MUST NOT requirements are explicit
all terminology is defined
the document is implementable without guessing
5.2 HARDENED → FROZEN
A document MAY be promoted to FROZEN only if:
test vectors exist for all critical rules
canonicalization is fully specified
error code mappings are stable
at least one reference implementation exists or is in progress
the downstream spec dependency chain is not broken
6. Versioning Rules
Each document MUST declare a version identifier:
v1
v2
v3
...
A version bump MUST occur if:
any MUST/MUST NOT rule changes
canonicalization changes
error mapping changes
validation logic changes
A version bump MAY occur for:
major restructuring
major clarifications
A version bump MUST NOT occur for:
formatting changes
spelling corrections
comment-only improvements
7. Normative Keyword Diff Guard
For FROZEN documents, CI SHOULD detect changes to normative keywords:
MUST
MUST NOT
SHALL
SHALL NOT
REQUIRED
If a FROZEN document changes these keywords, CI SHOULD fail.
8. Downstream Locking Rule
If a document is not at least HARDENED, downstream documents MUST NOT be promoted beyond DRAFT.
If an upstream document is HARDENED but not FROZEN, downstream documents MUST NOT be FROZEN.
9. Canonical Header Requirement
Every normative document MUST begin with a YAML header including:
state
version
Example:
Yaml
Kodu kopyala
---
state: HARDENED
version: v1
---
10. Enforcement Expectations
The repository SHOULD include CI enforcement that checks:
state header existence
invalid backward transitions
FROZEN file modifications
normative keyword diffs
This enforcement MAY be implemented in tools/.
END OF SPEC
