
---
state: DRAFT
version: v1.2
---

# ISC-CORE PROTOCOL MANIFEST

This document defines the canonical governance handshake contract for ISC Core.

It defines how external artifacts are evaluated, how verdicts are produced, and how determinism is preserved across independent receivers.

This is a protocol governance contract, not an implementation guide.

---

## 1. Purpose

The ISC Core repository is treated as a frozen genome.

Therefore:

- protocol evaluation MUST be deterministic
- governance outputs MUST be reproducible
- ambiguous interpretation MUST be treated as a failure condition
- stable output hashes MUST be environment-independent

This document defines the canonical boundary between:

- Producer systems (artifact emitters)
- Receiver systems (artifact evaluators)
- Governance artifacts (documents, specs, vectors)
- Governance verdicts (accept/reject/quarantine)

---

## 2. Definitions

### 2.1 Producer

A Producer is any system that emits an artifact intended to enter the ISC pipeline.

### 2.2 Receiver

A Receiver is any system that evaluates an artifact and produces a verdict.

A Receiver MUST apply this manifest deterministically.

### 2.3 Artifact

An Artifact is any candidate object submitted for evaluation.

Examples:

- normative document patch
- spec file
- test vector file
- canonicalization rule update
- governance metadata update

### 2.4 Verdict

A Verdict is the canonical evaluation result produced by a Receiver.

A Verdict MUST be machine-readable and stable under identical evaluation inputs.

---

## 3. Verdict Model

### 3.1 Verdict Types

A Receiver MUST output exactly one of the following verdict types:

- ACCEPT
- REJECT
- QUARANTINE

#### ACCEPT

The artifact is valid and MAY enter lineage.

#### REJECT

The artifact is invalid and MUST NOT enter lineage.

#### QUARANTINE

The artifact is not rejected, but cannot safely enter lineage yet.

A QUARANTINE verdict MUST NOT advance maturity state and MUST NOT be treated as lineage-valid.

---

## 4. Determinism Contract

### 4.1 Deterministic Evaluation Requirement

Given identical:

- artifact bytes
- artifact metadata bytes
- dependency graph
- dependency versions
- evaluation ruleset version
- time-source inputs (if applicable)

the Receiver MUST produce an identical deterministic verdict output.

### 4.2 Stable vs Audit Fields

A Verdict output contains:

- stable fields (deterministic)
- audit fields (non-deterministic)

Audit fields MUST NOT be included in any canonical verdict hash.

### 4.3 Verdict Hash Requirement

Each verdict MUST contain:

- verdict_hash

The verdict_hash MUST be computed from stable fields only.

The hashing algorithm MUST be SHA-256.

---

## 5. Artifact Metadata Location (Canonical)

### 5.1 Metadata Placement Rules

The location of artifact metadata MUST be canonical.

If metadata location is ambiguous, the Receiver MUST reject the artifact.

### 5.2 Markdown Artifacts

For Markdown artifacts (`.md` files), metadata MUST be stored in YAML frontmatter.

Example:

```yaml
---
state: DRAFT
version: v1
time_sensitive: false
dependencies: []
---
5.3 Non-Markdown Artifacts
For non-markdown artifacts (e.g. .json, .bin, .txt, .vec), metadata MUST be stored in a sidecar file:
<artifact_filename>.meta.yaml
Example:
vectors/case_001.bin
vectors/case_001.bin.meta.yaml
If a non-markdown artifact does not have a sidecar metadata file:
verdict MUST be QUARANTINE in DRAFT
verdict MUST be REJECT in HARDENED and FROZEN
5.4 Metadata Is Part of Artifact Identity
Metadata bytes MUST be considered part of the artifact identity.
Therefore:
artifact_identity_bytes MUST include both artifact bytes and metadata bytes
The concatenation MUST be length-prefixed.
Format:
uint64 big-endian length of artifact_bytes
artifact_bytes
uint64 big-endian length of meta_bytes
meta_bytes
If length-prefix format cannot be applied deterministically:
verdict MUST be REJECT
6. Canonical Artifact Identity
6.1 Artifact Hash
Each artifact MUST be identified by:
artifact_hash = SHA-256(artifact_identity_bytes)
Where artifact_identity_bytes is defined in Section 5.4.
6.2 Canonical Bytes Source
Canonical bytes and normalization MUST be defined by the rules in:
spec/core/DOC_FORMAT.md
If canonicalization rules are undefined or ambiguous:
the Receiver MUST output REJECT
7. Time, TTL, and Expiration
7.1 Time Sensitivity Flag
Each artifact MUST explicitly declare whether it is time sensitive.
This MUST be represented as a boolean:
time_sensitive: true|false
If time_sensitive is absent:
Receiver MUST treat it as false in DRAFT state
Receiver MUST reject in HARDENED and FROZEN state
7.2 Allowed Time Source Types
If time_sensitive = true, the Receiver MUST use one of the following time source types:
CI_INJECTED_UTC
WALLCLOCK_UTC
No other time source types are allowed unless introduced by a version bump.
If the Receiver cannot obtain a valid time source:
verdict MUST be QUARANTINE
7.3 Time Source Audit Fields
If time_sensitive = true, the Receiver MUST include the following audit fields:
time_source_type
time_source_id
time_source_id is an implementation-defined identifier.
It MUST NOT affect verdict_hash.
7.4 TTL Field
If time_sensitive = true, artifact MUST specify:
ttl_seconds
ttl_seconds MUST be an integer.
ttl_seconds MUST be greater than zero.
If ttl_seconds is missing while time_sensitive = true:
verdict MUST be REJECT
7.5 TTL Expiry Handling
If ttl_seconds is expired at evaluation time:
verdict MUST be REJECT
8. Ordering and Reorder Window
8.1 Canonical Ordering Rule
Receivers MUST apply strict in-order processing by default.
Out-of-order artifacts MUST NOT be ACCEPTed.
8.2 Reorder Window
If an artifact declares a reorder window, it MUST specify:
reorder_window_seconds
reorder_window_seconds MUST be an integer.
reorder_window_seconds MUST be greater than or equal to zero.
If reorder_window_seconds is absent:
reorder window is zero
8.3 Out-of-Order Handling
If an artifact arrives out-of-order but within reorder_window_seconds:
verdict MUST be QUARANTINE
If it arrives out-of-order and outside reorder_window_seconds:
verdict MUST be REJECT
Receiver MUST NOT choose alternate policies.
9. Dependency and Maturity Locking
9.1 Dependency Declaration Requirement
Every normative document MUST declare dependencies explicitly.
Dependency declaration MUST be machine-readable.
Dependencies MUST be declared even if empty.
Absence of dependency declaration MUST be treated as an error.
9.2 Dependency Format (Minimal Canonical Schema)
Dependencies MUST be expressed in YAML as:
Yaml
Kodu kopyala
dependencies:
  - "spec/core/STATE_MACHINE.md"
  - "spec/core/SEQUENTIAL_LOCK_RULE.md"
If dependencies is missing:
verdict MUST be QUARANTINE in DRAFT
verdict MUST be REJECT in HARDENED and FROZEN
If dependencies exists but is not a list of strings:
verdict MUST be REJECT
9.3 Dependency Lock Rule
Downstream documents MUST NOT advance beyond upstream maturity state.
Formal rule:
For any document B depending on A:
state(B) <= state(A)
9.4 Dependency Cycles
Circular dependencies MUST be detected.
If a dependency cycle exists:
verdict MUST be REJECT
9.5 Cycle Involvement Definition
"Involved documents" are defined as all nodes that are members of at least one directed cycle.
Only cycle-member nodes are considered involved.
Documents that merely reference a cycle-member but are not part of the cycle are not cycle-involved.
10. Evidence Requirements
10.1 Evidence Mandatory
Every verdict MUST include evidence.
Evidence MUST be present for:
ACCEPT
REJECT
QUARANTINE
10.2 Minimum Evidence Set
Each verdict MUST contain evidence for:
artifact_hash
ruleset_ref
dependency_snapshot_hash
evidence_hash
10.3 ruleset_ref Canonical Format
ruleset_ref MUST be a full git commit hash.
Allowed formats:
SHA-1: 40 lowercase hex characters
SHA-256: 64 lowercase hex characters
Branch names and tags MUST NOT be used.
10.4 Dependency Snapshot Hash
dependency_snapshot_hash MUST represent:
the full dependency graph
the version identifiers of all dependencies
the state of each dependency
dependency_snapshot_hash MUST be computed as:
SHA-256(canonical_dependency_snapshot_bytes)
canonical_dependency_snapshot_bytes MUST be deterministic.
Ordering MUST be lexicographic by document path.
10.5 evidence_hash
evidence_hash MUST be computed as:
SHA-256(canonical_evidence_bundle_bytes)
canonical_evidence_bundle_bytes MUST be deterministic.
If evidence cannot be canonicalized:
verdict MUST be REJECT
10.6 Evidence Reference (Audit Only)
A verdict MAY include:
evidence_ref
evidence_ref MUST be treated as an audit-only field.
It MUST NOT affect verdict_hash.
It MUST NOT affect ACCEPT/REJECT/QUARANTINE decisions.
evidence_ref MUST NOT contain environment-dependent data unless explicitly marked as audit-only.
11. Parser Determinism
11.1 Markdown Parser Requirement
Receivers MUST evaluate Markdown documents using a deterministic parser specification.
Receivers MUST be CommonMark compliant.
Receivers MUST NOT enable extensions unless explicitly allowed by an upstream frozen spec.
If parser compliance is unknown:
verdict MUST be QUARANTINE in DRAFT
verdict MUST be REJECT in HARDENED and FROZEN
11.2 YAML Frontmatter Parsing
If YAML frontmatter exists, it MUST be parsed in strict mode.
Strict mode means:
duplicate keys MUST be rejected
invalid YAML MUST be rejected
null vs absent MUST be distinguished
unknown YAML types MUST be rejected
If YAML cannot be parsed deterministically:
verdict MUST be REJECT
12. Null vs Absent Semantics
12.1 Canonical Interpretation
For all machine-readable fields:
absent means "not declared"
null means "explicitly declared as null"
These MUST NOT be treated as equivalent.
12.2 Governance Default Policy
Defaults MAY exist only if explicitly specified.
If a default is not specified:
absent MUST be treated as invalid in HARDENED and FROZEN state
13. Receiver Output Schema
13.1 Stable Fields (Included in verdict_hash)
Each verdict MUST contain the following stable fields:
verdict_type
artifact_hash
dependency_snapshot_hash
ruleset_ref
reason_code
evidence_hash
13.2 Audit Fields (Excluded from verdict_hash)
A verdict MAY contain the following audit fields:
evaluation_time_utc
receiver_id
receiver_version
debug_trace_ref
evidence_ref
time_source_type
time_source_id
Audit fields MUST NOT affect verdict_hash.
13.3 Canonical Stable Payload Encoding
The stable fields MUST be encoded as Canonical JSON before hashing.
Canonical JSON rules:
UTF-8 encoding
keys MUST be sorted lexicographically
no insignificant whitespace is allowed
no trailing newline is allowed
numeric values MUST be encoded deterministically
if a number cannot be represented deterministically, it MUST be encoded as a string
The stable payload MUST be encoded as:
Json
Kodu kopyala
{
  "artifact_hash": "...",
  "dependency_snapshot_hash": "...",
  "evidence_hash": "...",
  "reason_code": "...",
  "ruleset_ref": "...",
  "verdict_type": "..."
}
Field ordering in the JSON object MUST be lexicographic.
If stable payload encoding differs across receivers:
verdict MUST be QUARANTINE in DRAFT
verdict MUST be REJECT in HARDENED and FROZEN
13.4 verdict_hash Computation
verdict_hash MUST be computed as:
SHA-256(canonical_json_bytes)
14. Failure Handling
14.1 Reject vs Quarantine
REJECT MUST be used when:
determinism cannot be guaranteed in hardened contexts
canonical bytes cannot be derived
dependency cycles exist
maturity lock rule is violated
stable payload cannot be encoded deterministically
QUARANTINE MUST be used when:
artifact is potentially valid
but required evidence/time/order constraints are incomplete
and resolution may be possible later
14.2 No Silent Acceptance
If a Receiver cannot prove acceptance deterministically:
verdict MUST NOT be ACCEPT
15. State Machine Alignment
This manifest is downstream of:
spec/core/STATE_MACHINE.md
spec/core/SEQUENTIAL_LOCK_RULE.md
spec/core/DOC_FORMAT.md
If any rule conflicts, the following precedence order MUST apply:
STATE_MACHINE.md
SEQUENTIAL_LOCK_RULE.md
DOC_FORMAT.md
This document
16. Versioning Policy
16.1 Semantic Change
Any semantic change to this document MUST require a version bump.
16.2 Backward Compatibility
If version changes introduce stricter enforcement:
previous versions MAY still be referenced
but receivers MUST declare which version they implement via ruleset_ref
17. CI Enforcement Expectations
A CI pipeline SHOULD enforce:
dependency declarations exist
cycle detection
state locking rule
deterministic markdown parse safety
evidence completeness
stable payload canonical JSON hashing
If CI cannot enforce a rule automatically:
the rule MUST NOT be relied upon for HARDENED or FROZEN transitions
18. End of Document
This document is normative.
It is intended to be enforced by deterministic tooling.
Any ambiguity MUST be treated as a governance failure.
DENEME
TEST_CHANGE

