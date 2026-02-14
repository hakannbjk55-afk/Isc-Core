
---
state: DRAFT
version: v1
---

# ISC-CORE DOC FORMAT
Normative Document Template & Parsing Contract

This document defines the mandatory structure, markers, and parseable rules
for all normative Markdown documents under:
- `spec/`
- `docs/`

This is a governance + tooling contract. CI MAY enforce this document.

---

## 0. Scope

### 0.1 Applies To
This format applies to any `*.md` document under:
- `spec/`
- `docs/`

### 0.2 Does Not Apply To
This format does NOT apply to:
- source code files under `core/`
- scripts under `tools/`
- binary artifacts
- generated outputs

---

## 1. Frontmatter (REQUIRED)

### 1.1 Mandatory Frontmatter Block
Every normative document MUST begin with a YAML frontmatter block as the first bytes of the file:

```yaml
---
state: DRAFT
version: v1
---
1.2 Required Keys
Frontmatter MUST contain exactly these keys:
state: one of DRAFT | HARDENED | FROZEN
version: semantic identifier (e.g. v1, v1.1, v2)
1.3 Null/Absent Rules (Frontmatter)
If the frontmatter block is absent → CI MUST fail.
If state or version is absent → CI MUST fail.
state: null or version: null → CI MUST fail.
2. Title Rules (REQUIRED)
2.1 Single H1
Each document MUST contain exactly one H1 title (# ...) and it MUST appear after frontmatter.
2.2 Canonical Title Prefix
The H1 SHOULD start with ISC-CORE for core governance docs.
Example: # ISC-CORE STATE MACHINE
This is a SHOULD (not MUST) to avoid breaking older docs, but new core docs MUST comply.
3. Normative Keywords (REQUIRED)
3.1 Allowed Keywords
Normative language MUST use RFC-style keywords:
MUST, MUST NOT
SHALL, SHALL NOT
SHOULD, SHOULD NOT
MAY
REQUIRED
3.2 Keyword Casing
Normative keywords MUST be uppercase. Lowercase variants (e.g. "must") MUST NOT be used as normative statements.
3.3 Keyword Diff Guard Marker (for FROZEN)
If state: FROZEN, CI SHOULD enforce that normative keywords and requirement sentences are not modified without version bump rules (see §7).
4. Required Sections (Core Normative Docs)
For any document under spec/core/, the following sections MUST exist (as headings):
## 0. Scope
## 1. Definitions (if the doc introduces any new terms)
## N. Normative Requirements (the doc’s core MUST/SHALL rules)
## X. Dependencies (Governance Alignment)
## Y. Exit Criteria
## Z. Freeze Trigger
Notes:
Sections MAY be renumbered, but the headings MUST match textually.
If a doc does not need Definitions, it MUST include ## 1. Definitions and state "No new terms."
5. Dependencies Declaration (MUST, Parseable)
5.1 Mandatory Dependencies Section
Each normative document under spec/ and docs/ MUST include a dependencies section:
## X. Dependencies (Governance Alignment)
5.2 Canonical Dependency List Format
Dependencies MUST be declared as a bullet list of repo-relative paths.
Example:
spec/core/STATE_MACHINE.md
spec/core/SEQUENTIAL_LOCK_RULE.md
5.3 Absent vs Empty
If the Dependencies section is absent → CI MUST fail.
If the Dependencies section exists but is empty:
it MUST contain the literal text: No dependencies.
otherwise CI MUST fail.
5.4 No Semantic Dependencies
Dependencies MUST be explicit declarations only. Phrases like "depends on" in prose MUST NOT be used as the sole dependency mechanism.
6. Ambiguity Control (Determinism)
6.1 Forbidden Tokens in HARDENED/FROZEN
If state is HARDENED or FROZEN, the document MUST NOT contain:
TODO
TBD
???
FIXME
CI SHOULD enforce this by token scan.
6.2 Ambiguity Section (Optional but Enforceable)
Docs MAY include an ## Ambiguities section during DRAFT.
If present:
In HARDENED/FROZEN it MUST be either removed or contain only: None.
7. Versioning Rules (Normative)
7.1 Semantic Change Requires Version Bump
A semantic change MUST require a version bump.
Semantic change includes (non-exhaustive):
modifying MUST/SHALL requirements
changing validation outcomes
changing canonicalization behavior or bytes
changing default values (null vs absent semantics)
changing error precedence / classification
changing encoding rules that affect hashes/signatures
7.2 FROZEN Modification Rule
If a document is FROZEN, modifications MUST follow:
Create a new version (e.g. v2) OR
Create a new file path with version suffix if the repo policy requires it
Add/Update test vectors and migration notes where applicable
CI SHOULD flag edits to FROZEN docs that do not bump version.
8. Deterministic Ordering Rules
Where a document specifies lists (error codes, fields, reasons), it MUST define:
ordering rule (lexicographic / numeric / stable insertion)
how ties are resolved
whether duplicates are allowed
If ordering is undefined in a normative list:
CI SHOULD warn in DRAFT
CI MUST fail in HARDENED
9. Markdown Hygiene (Parse Safety)
9.1 Heading Integrity
Headings MUST be valid Markdown headings (#, ##, ###...). Broken lists that swallow headings are forbidden.
9.2 Code Fence Closure
All fenced code blocks MUST be properly closed. Unclosed fences MUST cause CI failure.
9.3 No Mixed List/Heading Corruption
A heading MUST NOT appear inside a bullet item unintentionally. If a heading line starts with whitespace that makes it part of a list, CI SHOULD fail.
10. Exit Criteria (for HARDENED)
A document MAY be promoted from DRAFT → HARDENED only if:
frontmatter is valid
required sections exist
dependencies are explicit and parseable
no forbidden tokens exist (TODO/TBD/???/FIXME)
normative requirements are complete and unambiguous
test vectors exist if the doc defines validation behavior
11. Freeze Trigger (for FROZEN)
A document MAY be promoted from HARDENED → FROZEN only if:
CI enforcement exists for this doc’s invariants
golden vectors exist and are stable (where applicable)
normative keyword diff guard is active
migration/versioning policy is satisfied
12. Dependencies (Governance Alignment)
This document depends on:
spec/core/STATE_MACHINE.md
spec/core/SEQUENTIAL_LOCK_RULE.md
This document MUST NOT advance beyond the maturity state of its upstream dependencies.
