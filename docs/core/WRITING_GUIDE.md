---
state: DRAFT
version: v1
---

# ISC-CORE WRITING GUIDE

This document defines the recommended writing practices for all ISC Core documents.

This is a documentation quality guide, not a normative protocol specification.

It exists to improve readability, reduce ambiguity, and prevent accidental drift by enforcing clarity.

This guide is downstream of:

- `spec/core/DOC_FORMAT.md`
- `spec/core/STATE_MACHINE.md`
- `spec/core/SEQUENTIAL_LOCK_RULE.md`

---

## 1. Purpose

The ISC Core is treated as a frozen genome.

Therefore, documentation quality is not optional.

Bad writing produces protocol ambiguity.
Protocol ambiguity produces implementation divergence.
Implementation divergence produces non-determinism.
Non-determinism destroys verification.

This guide exists to prevent that failure chain.

---

## 2. What This Guide Is

This guide is:

- a writing discipline contract
- a readability standard
- a clarity enforcement reference for reviewers
- a methodology for preventing semantic drift

This guide is NOT:

- a source of new normative protocol rules
- an implementation manual
- a replacement for RFC 2119 / RFC 8174 requirements

Normative requirements MUST only appear in `spec/` documents.

---

## 3. Writing Style Rules

### 3.1 Use Short Sentences

Avoid long sentences with multiple embedded clauses.

A good sentence has one idea.

Bad writing example:

> If the system receives a malformed packet that violates canonicalization rules and may affect the integrity chain, the verifier should attempt to recover unless the violation is severe.

Better writing:

> If the system receives a malformed packet, the verifier MUST reject it.
> Recovery is not allowed unless explicitly specified.

---

### 3.2 Avoid "Soft Language"

Do not use ambiguous language such as:

- "usually"
- "often"
- "should normally"
- "in most cases"
- "as needed"
- "it is recommended"

If a rule matters, it MUST be formalized.

If a rule does not matter, it SHOULD be removed.

---

### 3.3 Separate Normative vs Informative Content

Every document MUST separate:

- normative requirements (MUST / MUST NOT / SHOULD)
- informative explanations (examples, motivations, notes)

Use explicit labels:

- **Normative:**
- **Informative:**
- **Example:**
- **Note:**

This prevents accidental interpretation drift.

---

## 4. Ambiguity Elimination Discipline

### 4.1 Always Define Terms

Any new term introduced MUST be defined.

If a term is used without definition, it becomes a semantic attack surface.

Example:

Bad:

> The verifier may quarantine invalid data.

Good:

> **Quarantine** means: store the record for telemetry, but do not include it in the chain.

---

### 4.2 Avoid Undefined Defaults

Defaults are the most common source of protocol divergence.

If a field is optional, the spec MUST define:

- whether absence is allowed
- whether `null` is allowed
- whether empty string is allowed
- whether default substitution is allowed

If not defined, implementations will diverge.

---

### 4.3 Resolve Null vs Absent Explicitly

For every optional field, specify:

- `absent` behavior
- `null` behavior
- whether they are equivalent or not

If they are equivalent, state it explicitly.
If they are not equivalent, define the error behavior.

---

## 5. Determinism Hygiene

### 5.1 Deterministic Ordering Must Be Stated

Whenever a list exists, define:

- ordering rule (lexicographic / numeric / insertion-stable)
- tie-breaking rule
- whether duplicates are allowed
- whether stable serialization is required

If not defined, two implementations may produce different canonical bytes.

---

### 5.2 Deterministic Error Behavior Must Be Stated

Whenever an error is possible, define:

- the exact error code
- precedence rules if multiple errors exist
- whether the system must stop at first error or collect multiple errors

If error behavior is undefined, the verifier becomes non-deterministic.

---

## 6. Example Hygiene

### 6.1 Examples Must Be Explicitly Marked

All examples MUST be clearly labeled:

- Example
- Non-normative Example
- Informative Example

No example may be mistaken for a rule.

---

### 6.2 Examples Must Be Realistic

Examples should match real-world usage.

Bad example:

> user_id: "123"

Better example:

> user_id: "player_42"

---

### 6.3 Example Data Must Avoid Ambiguity

Avoid values that cause confusion:

- avoid `0`, `1`, `test`, `abc`
- avoid timestamps without timezone
- avoid hashes that are not valid length

Use full-length realistic placeholders.

---

## 7. Change Discipline

### 7.1 Always Write Change Impact Notes

Whenever a document changes, the author SHOULD describe:

- what changed
- why it changed
- which downstream documents may be impacted
- which vectors must be updated

This reduces silent drift.

---

### 7.2 Always Write Migration Notes When Needed

If a change breaks compatibility, the author SHOULD provide:

- migration path
- compatibility window if any
- deprecated behavior notes

---

## 8. Review Checklist

Before merging any document change, reviewers SHOULD verify:

- terminology is defined
- MUST/SHALL rules are unambiguous
- no "soft language" exists
- no undefined defaults exist
- null vs absent is specified
- ordering rules are specified
- error precedence is deterministic
- examples are labeled and non-normative
- no downstream document is stabilized beyond upstream maturity

---

## 9. Failure Modes This Guide Prevents

This guide exists to prevent:

- silent semantic drift
- multiple canonical byte interpretations
- incompatible verifier outputs
- implementation divergence
- protocol ambiguity becoming "policy"
- "it works on my machine" governance collapse

---

## 10. Final Rule

The ISC Core is not documentation.

It is executable law.

Writing must reflect that.