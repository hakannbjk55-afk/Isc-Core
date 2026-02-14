
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

State MUST be explicitly declared in YAML frontmatter.

State MUST NOT be implied by file location, commit history, or naming.

---

## 3. Frontmatter Requirements

Every document under `docs/` and `spec/` MUST begin with YAML frontmatter.

Example (this MUST be the very first bytes of the file):

```md
---
state: DRAFT
version: v1
---
3.1 Required Fields
Required fields:
state: one of DRAFT|HARDENED|FROZEN
version: semantic identifier such as v1, v2
3.2 Optional Fields
Optional fields:
upstreams: list of upstream doc paths (audit only)
last_hardened_commit: git SHA (audit only)
3.3 Enforcement Rule
If frontmatter is missing, CI MUST fail.
If state is missing, CI MUST fail.
If version is missing, CI MUST fail.
State MUST NOT be inferred by CI.
4. Allowed Transitions
State transitions are one-way only:
DRAFT -> HARDENED
HARDENED -> FROZEN
The following transitions are forbidden:
HARDENED -> DRAFT
FROZEN -> HARDENED
FROZEN -> DRAFT
State regression MUST NOT occur.
CI MUST reject forbidden transitions.
5. Transition Rules
5.1 DRAFT
DRAFT means the document is incomplete or evolving.
DRAFT documents MAY contain:
TODO markers
incomplete sections
placeholders
ambiguous language
DRAFT documents MUST still remain syntactically valid Markdown.
5.2 HARDENED
A document MAY be promoted to HARDENED only if all requirements below are satisfied.
5.2.1 Normative Completeness
The document MUST NOT contain open-ended placeholders such as:
TODO
TBD
???
later
to be decided
we will define
maybe
Exception: These markers are allowed inside fenced code blocks only.
CI MUST treat these markers as forbidden in prose.
5.2.2 Determinism
If the document defines parsing, serialization, canonicalization, hashing, signing, or validation rules, then it MUST define deterministic behavior.
The following MUST be explicitly specified:
byte ordering rules
field ordering rules
canonical encoding format
whitespace normalization rules (if relevant)
case sensitivity rules
5.2.3 Null vs Absent
If the document defines structured data, it MUST explicitly define:
how null is represented
how absence is represented
whether null and absent are equivalent or distinct
behavior on unexpected missing fields
5.2.4 Failure Modes
The document MUST enumerate failure modes.
Failure modes MUST be categorized:
parse-time errors
validate-time errors
canonicalize-time errors
verify-time errors
5.2.5 Forward Compatibility
The document MUST define behavior for:
unknown fields
unknown versions
extra trailing bytes
truncated data
5.2.6 Test Vectors
If the document defines a protocol format, it MUST be backed by golden test vectors.
Vectors MUST cover:
valid cases
invalid cases
encoding edge cases
ordering edge cases
null/absent ambiguity cases
truncation / tampering cases
unknown-field cases
5.3 FROZEN
A document MAY be promoted to FROZEN only if:
it is already HARDENED
it has complete vectors
it has determinism guarantees
CI enforcement exists
Once a document is FROZEN, its semantics MUST NOT change.
6. Frozen Change Policy
6.1 Editorial Changes
Editorial-only changes are allowed in FROZEN documents.
Editorial-only changes include:
typos
formatting fixes
clarifications that do not change normative meaning
additional non-normative examples
Editorial changes MUST NOT change behavior.
6.2 Semantic Changes
Semantic changes are forbidden in FROZEN documents.
Semantic changes include:
modifying MUST / MUST NOT requirements
changing encoding rules
changing canonicalization
changing validation outcomes
changing error behavior
Semantic changes require:
a new version (v2, v3, ...)
new vectors
migration notes
7. Normative Keyword Diff Guard
For FROZEN documents, CI SHOULD detect changes to normative keywords:
MUST
MUST NOT
SHALL
SHALL NOT
REQUIRED
If these change, the change MUST be treated as semantic unless explicitly reviewed.
8. Repository-Wide State Invariant
At any time:
a document MUST have exactly one state
state MUST be explicitly declared
state MUST NOT be inferred
This process MUST be machine-enforceable.
