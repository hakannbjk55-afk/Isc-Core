
---
state: DRAFT
version: v1.1
---

# ISC-CORE SEQUENTIAL LOCK RULE

This document defines the canonical upstream/downstream locking rule for the ISC Core repository.

It enforces strict sequential stabilization:
downstream documents MUST NOT advance beyond the maturity state of their upstream documents.

This is a protocol governance contract, not an implementation guide.

---

## 1. Purpose

ISC-CORE is treated as a **frozen genome**.

Its normative documents define deterministic behavior and MUST NOT drift.
Therefore, the repository MUST enforce a strict writing and freezing order.

This rule prevents:

- premature freezing of dependent specs
- inconsistent requirements across files
- silent divergence of canonical formats
- "spec debt" hidden behind downstream assumptions

---

## 2. Definitions

### 2.1 Normative Document

A "normative document" means any `.md` file under `docs/` or `spec/`
that defines requirements, formats, invariants, validation rules,
canonicalization, signing rules, or protocol semantics.

### 2.2 Upstream Document

A document **A** is an upstream document of **B** if **B declares A**
as an upstream dependency.

Upstream relationships MUST be declared explicitly.
They MUST NOT be inferred from prose references.

### 2.3 Downstream Document

A document **B** is downstream of **A** if B declares A as an upstream dependency.

### 2.4 Maturity States

Documents MUST use the canonical lifecycle state machine:

- DRAFT
- HARDENED
- FROZEN

(See: `spec/core/STATE_MACHINE.md`)

### 2.5 State Ordering

The maturity ordering MUST be interpreted as:

- DRAFT = 0
- HARDENED = 1
- FROZEN = 2

This ordering MUST be used for all CI enforcement.

---

## 3. Dependency Declaration Requirements

### 3.1 Canonical Declaration Format

All normative documents MUST declare upstream dependencies in YAML frontmatter.

Example:

```md
---
state: DRAFT
version: v1
upstreams:
  - spec/core/STATE_MACHINE.md
  - spec/core/CANONICALIZATION.md
---
3.2 Required Behavior
The upstreams field MUST exist in frontmatter.
If the document has no upstream dependencies, upstreams MUST be an empty list.
Example:
Yaml
Kodu kopyala
upstreams: []
3.3 Null vs Absent Rule
upstreams: [] means the document has no upstream dependencies.
Missing upstreams field MUST be treated as invalid.
upstreams: null MUST be treated as invalid.
CI MUST fail if upstreams is absent or null.
3.4 Canonical Path Rules
Each entry in upstreams MUST be:
a repository-relative POSIX path
pointing to an existing .md file
without leading /
without .. path traversal
case-sensitive
CI MUST fail on invalid paths.
4. Core Rule
4.1 Sequential Lock Constraint
A downstream document MUST NOT advance to a higher maturity state than any of its upstream documents.
Formally:
If:
B declares A in upstreams
Then:
state(B) <= state(A)
Where ordering is:
DRAFT < HARDENED < FROZEN
CI MUST enforce this constraint.
5. Allowed Transitions
5.1 DRAFT → HARDENED
A document MAY transition from DRAFT to HARDENED only if:
all upstream dependencies are at least HARDENED
the document contains no TODO/TBD markers in prose
all normative requirements are complete
all failure modes are enumerated
canonicalization rules (if defined) are deterministic
test vectors exist if the document defines a format
5.2 HARDENED → FROZEN
A document MAY transition from HARDENED to FROZEN only if:
all upstream dependencies are FROZEN
all required test vectors exist
canonical format rules are complete and deterministic
validation rules are complete
error behavior is stable
CI enforcement exists for all MUST/MUST NOT constraints
6. Forbidden Transitions
The following MUST be rejected:
DRAFT → FROZEN
HARDENED → DRAFT
FROZEN → HARDENED
FROZEN → DRAFT
CI MUST fail if forbidden transitions occur.
7. Dependency Graph Invariants
7.1 Cycle Detection
The upstream dependency graph MUST be acyclic.
Circular dependencies MUST be treated as fatal.
Example invalid graph:
A depends on B
B depends on A
CI MUST detect cycles and MUST fail.
7.2 Duplicate Dependencies
Duplicate entries in upstreams MUST be rejected.
CI MUST fail.
7.3 Self Dependency
A document MUST NOT list itself as an upstream.
CI MUST fail.
8. Semantic Change Rule
8.1 Definition
A semantic change is any modification that can alter behavior in:
parsing
canonicalization
serialization
hashing
signing
validation outcomes
error precedence or error ordering
default values
implicit field insertion
null vs absent behavior
unknown-field behavior
version negotiation behavior
8.2 Frozen Rule
If a document is FROZEN, semantic changes are forbidden.
Editorial-only changes MAY be allowed, but MUST NOT alter normative meaning.
8.3 Semantic Change Handling
If semantic changes are required, the following MUST occur:
a new version MUST be created (v2, v3, ...)
new test vectors MUST be provided
migration notes MUST be added
9. Downstream Revalidation Requirement
9.1 Revalidation Trigger
If an upstream document changes in a semantic way, all downstream documents MUST be revalidated.
9.2 No State Regression Guarantee
This revalidation requirement MUST NOT be implemented by state regression.
Specifically:
HARDENED documents MUST NOT be forced back to DRAFT
FROZEN documents MUST NOT be altered without version bump
Instead, CI MUST enforce that downstream documents:
are updated if needed
or explicitly confirmed as unaffected
10. CI Enforcement Rules
CI MUST enforce:
presence of YAML frontmatter
state existence and validity
version existence and validity
upstreams existence (including empty list case)
upstream file existence
no cycles in dependency graph
sequential lock constraint: state(B) <= state(A)
CI MUST fail on any violation.
CI MUST NOT infer dependencies from prose.
11. Normative Keyword Diff Guard
For FROZEN documents, CI SHOULD detect changes to normative keywords:
MUST
MUST NOT
SHALL
SHALL NOT
REQUIRED
Any change affecting these keywords MUST be treated as semantic unless explicitly reviewed.
12. Exit Criteria
This document MAY be promoted to HARDENED only if:
dependency declaration format is stable
CI implementation exists for all MUST rules
cycle detection is implemented
This document MAY be promoted to FROZEN only if:
CI enforcement is present in repository pipelines
dependency graph behavior is stable and deterministic
all edge cases are covered by tests
