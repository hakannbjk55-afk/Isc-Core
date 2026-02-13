state: HARDENED version: v1
ISC-CORE STATE MACHINE
This document defines the canonical lifecycle state machine for all normative documents in this repository.
This is a process contract, not a protocol specification.
1. Scope
This state machine applies to all .md documents under:
docs/
spec/
It does NOT apply to:
source code files under core/
tooling scripts under tools/
binary artifacts
2. States
Each document MUST be in exactly one of the following states:
DRAFT
HARDENED
FROZEN
State MUST be explicitly declared in YAML frontmatter.
State MUST NOT be implied by file location, commit history, or naming.
3. YAML Frontmatter Requirements (Canonical)
3.1 Delimiter Rules
Every governed document MUST begin with YAML frontmatter.
The very first bytes of the file MUST be:
---\n
The YAML frontmatter MUST terminate with:
---\n
No bytes may appear before the opening delimiter.
UTF-8 BOM MUST NOT be present.
3.2 YAML Validity
Frontmatter MUST be valid YAML 1.2.
Duplicate keys MUST NOT be permitted. If duplicate keys are detected, CI MUST fail.
3.3 Required Fields
Required fields:
state
version
If state is missing, CI MUST fail.
If version is missing, CI MUST fail.
3.4 State Field Rules
state MUST be exactly one of:
DRAFT
HARDENED
FROZEN
State MUST be uppercase.
Any other value MUST fail CI.
3.5 Version Field Rules
version MUST match the regex:
^v[0-9]+$
Examples of valid versions:
v1
v2
v10
Examples of invalid versions:
1
v1.0
v1-final
banana
3.6 Optional Fields
Optional fields:
upstreams
last_hardened_commit
If upstreams is present, it MUST be a YAML sequence (list).
Each upstream entry MUST be a relative POSIX-style path string.
Example:
Yaml
Kodu kopyala
upstreams:
  - docs/core/ROADMAP.md
  - spec/core/SEQUENTIAL_LOCK_RULE.md
4. Allowed Transitions
State transitions are one-way only:
DRAFT -> HARDENED
HARDENED -> FROZEN
The following transitions are forbidden:
HARDENED -> DRAFT
FROZEN -> HARDENED
FROZEN -> DRAFT
State regression MUST NOT occur.
5. State Regression Detection (CI Source of Truth)
CI MUST validate state transitions by comparing the new document state against the previous committed state of the same file in the target branch (e.g. main).
Rules:
If the file does not exist in the target branch, it is treated as a new document.
If the file exists, CI MUST read the previous state from its YAML frontmatter.
If the new state represents a forbidden transition relative to the previous state, CI MUST fail.
This is not inference. The target branch is the canonical historical source of truth.
6. Meaning of Each State
6.1 DRAFT
DRAFT means the document is incomplete or evolving.
DRAFT documents MAY contain:
TODO markers
incomplete sections
placeholders
ambiguous language
DRAFT documents MUST still remain syntactically valid Markdown.
6.2 HARDENED
A document MAY be promoted to HARDENED only if all HARDENED requirements are satisfied.
HARDENED documents MUST NOT contain unresolved ambiguity.
HARDENED documents SHOULD change rarely.
6.3 FROZEN
A document MAY be promoted to FROZEN only if:
it is already HARDENED
it has complete vectors (if applicable)
it has determinism guarantees
CI enforcement exists
Once a document is FROZEN, its semantics MUST NOT change.
7. Placeholder Marker Rules (TODO/TBD)
HARDENED and FROZEN documents MUST NOT contain placeholder markers in prose.
Forbidden markers include:
TODO
TBD
???
later
to be decided
we will define
maybe
CI scanning MUST be:
case-insensitive
word-boundary aware
Exception: Markers inside fenced code blocks are allowed.
CI MUST ignore fenced code blocks using a CommonMark-compliant parser.
8. Frozen Change Policy
8.1 Editorial Changes
Editorial-only changes are allowed in FROZEN documents.
Editorial-only changes include:
typos
formatting fixes
clarifications that do not change normative meaning
additional non-normative examples
Editorial changes MUST NOT change behavior.
8.2 Semantic Changes
Semantic changes are forbidden in FROZEN documents.
Semantic changes include:
modifying MUST / MUST NOT requirements
changing encoding rules
changing canonicalization rules
changing validation outcomes
changing error behavior
Semantic changes require:
a new version (v2, v3, ...)
new vectors
migration notes
9. Normative Keyword Diff Guard
For FROZEN documents, CI SHOULD detect changes to normative keywords:
MUST
MUST NOT
SHALL
SHALL NOT
REQUIRED
If these change, the change MUST be treated as semantic unless explicitly reviewed.
10. Repository-Wide State Invariant
At any time:
a document MUST have exactly one state
state MUST be explicitly declared
state MUST NOT be inferred
This process MUST be machine-enforceable.
11. References
docs/core/ROADMAP.md
spec/core/SEQUENTIAL_LOCK_RULE.md
spec/core/FREEZE_POLICY.md