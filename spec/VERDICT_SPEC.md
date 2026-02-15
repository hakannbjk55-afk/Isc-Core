
---
state: DRAFT
version: v1.3
---

# ISC-CORE VERDICT SPEC

This document defines the canonical verdict evaluation contract for ISC Core.

It specifies how external artifacts MUST be evaluated, how deterministic verdicts MUST be produced, and how stable verdict hashes MUST remain reproducible across independent receivers.

This is a protocol governance contract, not an implementation guide.

This document is downstream of:

- spec/core/STATE_MACHINE.md
- spec/core/SEQUENTIAL_LOCK_RULE.md
- spec/core/DOC_FORMAT.md
- spec/core/PROTOCOL_MANIFEST.md

---

## 1. Purpose

The ISC Core repository is treated as a frozen genome.

Therefore:

- evaluation MUST be deterministic
- verdict outputs MUST be reproducible
- ambiguous interpretation MUST be treated as a failure condition
- stable output hashes MUST be environment-independent
- all canonical hash algorithms MUST be explicitly specified

---

## 2. Scope

This specification governs:

- receiver evaluation of artifacts
- dependency resolution behavior
- verdict output structure
- stable vs audit fields
- canonical hash computation rules

This specification does NOT define:

- implementation code architecture
- internal receiver storage layout
- UI rendering of verdicts

---

## 3. Definitions

### 3.1 Artifact

An artifact is any input object evaluated by a receiver.

Artifacts may include:

- markdown documents
- protocol specs
- test vector bundles
- patches
- structured metadata payloads

### 3.2 Receiver

A receiver is any system that evaluates an artifact and produces a verdict.

### 3.3 Verdict

A verdict is the final classification of an artifact under the ISC Core governance contract.

Verdict values are:

- ACCEPT
- REJECT
- QUARANTINE

### 3.4 Deterministic Completion

Deterministic completion means:

- identical artifact bytes
- identical declared dependencies
- identical dependency snapshots
- identical ruleset version
- identical time-source inputs (when applicable)

MUST yield identical verdict and identical stable verdict_hash.

---

## 4. Canonical Pipeline (Mandatory Order)

Receivers MUST evaluate artifacts using the following pipeline order.

No step MAY be skipped.

1. Artifact byte ingestion
2. Canonical byte normalization (DOC_FORMAT)
3. Metadata extraction
4. Dependency extraction
5. Dependency snapshot resolution
6. Ordering + reorder enforcement
7. TTL evaluation (if applicable)
8. Rule evaluation + validation
9. Verdict output emission

If any step fails to complete deterministically, the receiver MUST produce QUARANTINE or REJECT as defined by this spec.

---

## 5. Stable vs Audit Fields

### 5.1 Stable Fields

Stable fields MUST affect verdict_hash.

Stable fields MUST be fully deterministic.

Stable fields MUST NOT contain environment-dependent identifiers.

### 5.2 Audit Fields

Audit fields MUST NOT affect verdict_hash.

Audit fields MAY contain timestamps, file paths, runtime traces, and receiver-local diagnostics.

---

## 6. Artifact Metadata Contract

### 6.1 Artifact Type

Each artifact MUST declare its type explicitly.

Artifact type inference MUST NOT be used.

If artifact_type is absent, the receiver MUST REJECT.

### 6.2 Metadata Location Canonicalization

Metadata MUST be stored in one of the following canonical locations:

- Markdown artifacts MUST use YAML frontmatter.
- Non-markdown artifacts MUST use a sidecar metadata file named:
  `<artifact_name>.meta.yaml`

If metadata cannot be extracted from the canonical location, the receiver MUST QUARANTINE (Q150).

### 6.3 time_sensitive Flag

Each artifact MUST declare:

- time_sensitive: true|false

If absent:

- in DRAFT receiver MAY warn
- in HARDENED receiver MUST QUARANTINE (Q150)
- in FROZEN receiver MUST REJECT

---

## 7. Verdict Types

### 7.1 ACCEPT

ACCEPT MUST only be returned if:

- no rule violation exists
- dependency resolution succeeded deterministically
- reorder constraints are satisfied
- TTL is not expired (if applicable)
- canonical bytes are parse-safe
- no QUARANTINE trigger applies

### 7.2 REJECT

REJECT MUST be returned if:

- canonical bytes are invalid under DOC_FORMAT
- required metadata fields are missing (artifact_type, versioning fields, etc.)
- dependency cycles are detected
- TTL expired under verifiable time source
- a MUST/SHALL rule is violated

### 7.3 QUARANTINE

QUARANTINE MUST be returned if evaluation cannot safely complete deterministically.

QUARANTINE MUST NOT be used as a catch-all.

QUARANTINE MUST only be returned under enumerated trigger codes defined in Section 11.

---

## 8. Dependency Contract

### 8.1 Dependency Declaration

Each artifact MUST declare dependencies explicitly, even if empty.

The dependency declaration MUST be machine-readable.

If dependency declaration is absent:

- in DRAFT receiver SHOULD warn
- in HARDENED receiver MUST fail evaluation (Q120)
- in FROZEN receiver MUST REJECT

### 8.2 Dependency Schema

Dependencies MUST be expressed as a machine-readable list.

Dependency list semantics MUST be order-insensitive.
Receivers MUST NOT treat author-provided list order as meaningful.

Each dependency entry MUST contain:

- path (string)
- version (string)

Canonical form MUST be:

```yaml
dependencies:
  - path: spec/core/STATE_MACHINE.md
    version: v1.0
  - path: spec/core/SEQUENTIAL_LOCK_RULE.md
    version: v1.1
If dependencies exist but are malformed, receiver MUST QUARANTINE (Q120).
8.3 Dependency Version Resolution
Dependency versions MUST be exact.
Version ranges MUST NOT be used.
If a dependency version cannot be resolved exactly, receiver MUST QUARANTINE (Q120).
If multiple versions satisfy the same declared dependency (ambiguity), receiver MUST REJECT.
8.4 Dependency Snapshot Hash
Receiver MUST compute a dependency_snapshot_hash using canonical JSON encoding (RFC 8785).
The dependency snapshot MUST be represented as:
Json
Kodu kopyala
{
  "dependencies": [
    "spec/core/SEQUENTIAL_LOCK_RULE.md@v1.1",
    "spec/core/STATE_MACHINE.md@v1.0"
  ]
}
The array MUST be sorted lexicographically.
Hash algorithm MUST be SHA-256.
dependency_snapshot_hash MUST be expressed as:
sha256:<64 lowercase hex>
9. Reorder Rules
9.1 Canonical Reorder Policy
Receiver behavior for reorder violations MUST be canonical.
Receivers MUST enforce strict in-order processing.
Out-of-order artifacts MUST result in QUARANTINE (Q130).
Receiver choice is not allowed.
9.2 Reorder Window
Reorder window MUST be defined by PROTOCOL_MANIFEST.
If reorder_window is absent, default MUST be 0.
10. TTL Rules
10.1 TTL Presence
If ttl_seconds is absent, TTL MUST be treated as disabled.
TTL evaluation MUST only occur if:
time_sensitive = true
ttl_seconds is present
10.2 Time Source Requirement
TTL evaluation MUST only be performed using an approved time source type.
Allowed time_source_type values:
CI_INJECTED_UTC
TSA_SIGNED_UTC
If time_sensitive = true and ttl_seconds exists, but time_source_type is missing or invalid, receiver MUST QUARANTINE (Q100).
10.3 TTL Expiration Behavior
If TTL is expired at evaluation time under an approved time source, receiver MUST REJECT.
Receiver MUST emit audit fields describing evaluation_time.
evaluation_time MUST NOT affect verdict_hash.
11. QUARANTINE Trigger Codes (Canonical List)
Receiver MUST return QUARANTINE only if at least one of the following trigger codes applies:
Q100: TIME_SOURCE_MISSING_FOR_TIME_SENSITIVE
Q110: TIME_SOURCE_UNVERIFIABLE
Q120: DEPENDENCY_RESOLUTION_INCOMPLETE
Q130: REORDER_OUT_OF_ORDER
Q140: RECEIVER_RESOURCE_LIMIT_EXPLICIT
Q150: METADATA_LOCATION_INVALID
Q160: CANONICAL_PARSE_UNSAFE_BUT_RECOVERABLE
Any condition outside this list MUST NOT produce QUARANTINE.
If a receiver cannot classify the failure, it MUST REJECT.
12. Reason Codes
12.1 Reason Code Namespaces
Reason codes MUST be namespaced:
E*** codes MUST imply REJECT
Q*** codes MUST imply QUARANTINE
W*** codes MUST imply ACCEPT with warnings
Mixing namespaces is allowed only if the final verdict is consistent with the strongest code class.
Precedence:
REJECT dominates QUARANTINE dominates ACCEPT.
12.2 Reason Object Schema
Receivers MAY emit structured reasons.
Reason objects MUST have:
code (string)
message (string, audit only)
Reason objects MAY include:
path (audit only)
details (audit only)
12.3 Deterministic Meaning
Only reason.code values are allowed to influence stable verdict hashing.
All other reason fields are audit-only.
13. Verdict Output Object
13.1 Output Structure
The verdict output MUST be emitted as a JSON object.
Receiver MUST output a verdict object containing:
Stable fields:
verdict
artifact_hash
ruleset_id
dependency_snapshot_hash
reason_codes
verdict_hash
Audit fields:
receiver_id
evaluation_time
evidence_ref
debug_trace
reason_objects
13.2 evidence_ref Rules
evidence_ref MUST be treated as audit-only.
evidence_ref MUST NOT affect verdict_hash.
If evidence material is required, the receiver MUST include:
evidence_hash (SHA-256)
evidence_hash is stable.
13.3 ruleset_id Rules
ruleset_id MUST be canonical.
ruleset_id MUST be expressed as exactly 40 lowercase hex characters with no prefix.
Tags, branches, and semver labels MUST NOT be used.
If ruleset_id is not canonical, receiver MUST REJECT.
14. Verdict Hash Input Object (VHI)
14.1 Definition
verdict_hash MUST be computed ONLY over the Verdict Hash Input Object (VHI).
The VHI MUST be a canonical JSON object with EXACT keys:
verdict
artifact_hash
ruleset_id
dependency_snapshot_hash
reason_codes
No other keys are allowed.
14.2 Canonical Encoding
The VHI MUST be encoded using RFC 8785 JSON Canonicalization Scheme.
Encoding MUST be UTF-8.
Hash algorithm MUST be SHA-256.
14.3 reason_codes Ordering
reason_codes MUST be:
an array of strings
sorted lexicographically
duplicates MUST be removed
Duplicate presence MUST NOT change the final normalized reason_codes set.
14.4 Example VHI
Json
Kodu kopyala
{
  "verdict": "QUARANTINE",
  "artifact_hash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "ruleset_id": "0123456789abcdef0123456789abcdef01234567",
  "dependency_snapshot_hash": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "reason_codes": ["Q130"]
}
verdict_hash MUST be the SHA-256 hash of the RFC 8785 canonical bytes of this object.
15. Artifact Hash Rules
artifact_hash MUST be computed from canonical bytes.
Canonical bytes MUST follow DOC_FORMAT.
Hash algorithm MUST be SHA-256.
artifact_hash MUST be expressed as:
sha256:<64 lowercase hex>
16. Canonical Parser Requirements
16.1 Markdown Parsing
Markdown parsing MUST follow:
CommonMark v0.30
no extensions
Frontmatter MUST be YAML only.
Line endings MUST be normalized to LF before hashing.
16.2 Parse Failure Handling
If markdown parsing fails deterministically, receiver MUST REJECT.
If parsing is ambiguous due to malformed structure but recovery is possible, receiver MUST QUARANTINE (Q160).
17. Cycle Detection
17.1 Rule
Dependency cycles MUST be rejected.
Cycle detection MUST be performed on the declared dependency graph.
17.2 Impact Marking
All documents that are nodes inside the detected cycle MUST be marked as involved.
All involved documents MUST be REJECTED.
Documents outside the cycle MUST NOT be rejected due to cycle membership.
18. Determinism Guarantees
If two receivers are compliant with this spec, then:
identical artifact canonical bytes
identical dependency versions
identical dependency snapshots
identical ruleset_id
identical reorder state
identical time_source inputs
MUST produce identical:
verdict
reason_codes
dependency_snapshot_hash
verdict_hash
Audit fields MAY differ.
19. Backward Compatibility
If a semantic change occurs, a new version MUST be issued.
Frozen versions MUST NOT be modified.
If a frozen verdict rule changes, it MUST be introduced as a new versioned document.
20. Compliance Requirements
A receiver is compliant only if it:
enforces the pipeline order
produces verdict_hash only from VHI
uses RFC 8785 canonical JSON
uses SHA-256 for all hashes
enforces the QUARANTINE trigger list
enforces exact dependency version resolution
enforces canonical ruleset_id format
enforces CommonMark v0.30 no-extension parsing
Any deviation MUST be treated as a governance violation.
21. Final Rule
Any ambiguity not explicitly resolved by this document MUST be treated as a failure condition.
In DRAFT, failure MAY produce QUARANTINE.
In HARDENED, failure MUST produce QUARANTINE or REJECT depending on the relevant trigger class.
In FROZEN, ambiguity MUST produce REJECT.
