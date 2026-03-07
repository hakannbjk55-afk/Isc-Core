# ISC Core Governance Specification

## 1. Purpose

ISC Core governance defines how a verifier decides whether an evidence pack was signed by an authorized trust context.

Its purpose is to make signature verification portable, policy-aware, and durable over time without requiring a centralized metadata server.

ISC Core governance is inspired by TUF-style trust root and signer authorization models, but differs in one critical way:

> the trust context is carried with the pack, not fetched from a live service.

This allows verification to remain possible even if the original platform, CI system, or hosted verification service no longer exists.

---

## 2. Scope

This specification defines:

- governance objects used by ISC Core
- how allowed signers are represented
- how revocation is represented
- how key rotation is represented
- how a verifier evaluates governance state
- how governance participates in offline verification

This specification does **not** define:

- user identity systems
- certificate authority models
- transparency log protocols
- blockchain anchoring formats
- organization-level access control outside the pack

---

## 3. Design Goals

ISC Core governance is designed to provide:

1. **Portable trust**
   Trust metadata must be usable offline.

2. **Verifier-local decision making**
   A verifier should not need a metadata server to determine whether a signer was authorized.

3. **Explicit revocation**
   Revoked signers must be representable and machine-checkable.

4. **Key rotation support**
   Governance must support signer replacement over time.

5. **Minimal trust surface**
   Verification should depend on a small, explicit set of trust assumptions.

6. **Durable auditability**
   Governance state should remain inspectable long after the original system disappears.

---

## 4. Governance Model Overview

ISC Core uses a portable governance model built around a trust root and signer authorization state.

At a high level, verification evaluates:

- what keys are allowed
- what keys are revoked
- whether the pack signature was made by an allowed signer
- whether the signer was revoked at verification time
- whether governance state is internally valid

The pack therefore carries not only evidence, but also the policy context required to evaluate that evidence.

This makes ISC Core governance:

- closer to TUF than to Git-style bare key lists
- simpler than identity-and-certificate systems like Sigstore
- independent of a mandatory metadata server

---

## 5. Governance Objects

An ISC Core governance context may include the following objects.

### 5.1 Trust Root

The trust root defines the initial trusted governance authority.

It may contain:

- root public keys
- governance version
- threshold rules, if supported
- root metadata hash
- optional creation metadata

The trust root is the starting point from which governance validity is evaluated.

### 5.2 Allowed Signers

Allowed signers are the public keys or signer identifiers authorized to sign packs under the current governance state.

An allowed signer entry may include:

- signer key ID
- public key material
- signer label or role
- activation version or timestamp
- optional metadata

### 5.3 Revocation Set

The revocation set defines which signers are no longer trusted.

A revocation entry may include:

- signer key ID
- revocation reason
- revocation version
- revocation time, if available
- optional replacement metadata

### 5.4 Rotation Metadata

Rotation metadata links previous trust state to current trust state.

It may define:

- old signer key ID
- new signer key ID
- rotation event version
- governance continuity link
- optional proof or signature chain

### 5.5 Governance Manifest

A governance manifest binds the governance files together so a verifier can evaluate them as a coherent set.

It may include:

- file list
- hashes
- governance version
- optional parent governance version
- canonical ordering rules

---

## 6. Trust Root Semantics

ISC Core governance begins from an explicitly trusted root.

The verifier must obtain that root through one of the following means:

- bundled governance state included in the pack
- verifier-local trust store
- previously trusted governance state
- an application-defined out-of-band trust root

ISC Core does not define one universal distribution mechanism for the initial root.
It only defines how the root is interpreted once obtained.

### 6.1 Root Validity

A root is considered valid if:

- its structure is syntactically correct
- required fields are present
- its signatures satisfy root policy, if applicable
- it hashes correctly under canonical rules
- it is accepted by the verifier’s trust policy

### 6.2 Root as Trust Boundary

The trust root is the governance security boundary.

If the trust root is malicious, replaced, or incorrectly trusted, governance verification may still succeed while representing the wrong authority.

Therefore, the initial trust root remains an explicit trust assumption.

---

## 7. Allowed Signers

An allowed signer is any signer recognized by the current governance state as authorized to sign an ISC evidence pack.

### 7.1 Minimum Allowed Signer Semantics

At minimum, an allowed signer must be represented by:

- stable signer identifier
- public verification key
- governance membership state

### 7.2 Optional Signer Metadata

Optional metadata may include:

- human-readable label
- signer role
- owner system
- environment label
- activation metadata

This metadata is useful for audit readability but is not required for cryptographic validity.

### 7.3 Verification Rule

A pack signature satisfies signer authorization if:

- the signature verifies cryptographically, and
- the signer is present in the allowed signer set, and
- the signer is not listed in the revocation set, and
- governance state itself is valid

---

## 8. Revocation

Revocation allows previously trusted signers to be marked untrusted.

This is necessary for:

- key compromise
- signer retirement
- governance change
- incident response
- operator error correction

### 8.1 Revocation Semantics

A signer is revoked when governance state explicitly marks that signer as no longer authorized.

A verifier must treat a revoked signer as unauthorized unless local verification policy explicitly allows historical acceptance rules.

### 8.2 Historical Behavior

Implementations may distinguish between:

- **current validity**
- **historical validity at signing time**

This specification allows such distinction, but does not require a single universal policy for all deployments.

A verifier must therefore clearly state which revocation mode it applies.

### 8.3 Offline Constraint

Offline verification can only evaluate revocation state that is available to the verifier.

ISC Core therefore requires revocation data to be carried with or available beside the pack if offline governance-aware verification is expected.

---

## 9. Key Rotation

Key rotation allows governance continuity without breaking the verification model.

Rotation is expected in cases such as:

- planned key lifecycle renewal
- signer replacement
- compromise recovery
- governance restructuring

### 9.1 Rotation Goal

Rotation must allow a verifier to understand that trust moved from one signer or root state to another without requiring a live metadata service.

### 9.2 Rotation Semantics

A valid rotation event should allow the verifier to determine:

- what trust state existed before
- what trust state exists after
- whether the transition is authorized
- whether continuity was preserved

### 9.3 Rotation Failure

If a verifier cannot establish valid continuity between governance states, verification should fail or degrade according to local policy.

---

## 10. Verification Rules

ISC Core governance verification is performed as part of pack verification.

A governance-aware verifier should evaluate, in order:

1. governance files exist and are structurally valid
2. governance hashes and manifest bindings are valid
3. trust root is acceptable
4. signer set is derivable from governance state
5. revocation set is derivable from governance state
6. pack signatures verify cryptographically
7. each required signer is currently authorized under governance rules
8. no required signer is revoked under applied policy

If these checks succeed, governance verification succeeds.

---

## 11. Offline Verification Behavior

ISC Core governance is specifically designed for offline use.

This means a verifier should be able to determine signer authorization without fetching:

- live signer lists
- live policy documents
- hosted metadata
- certificate status
- transparency log state

This property is what makes governance portable.

### 11.1 Offline Guarantee

If the verifier has:

- the pack
- the governance material
- the trust root
- the verification binary

then governance-aware verification should be possible offline.

### 11.2 Offline Limitation

Offline verification only knows what governance state it has been given.

It cannot discover newer revocations, newer rotations, or newer governance updates unless those were included or otherwise supplied.

This is an intentional tradeoff in favor of portability.

---

## 12. Failure Cases

Governance verification must fail, or be reported as invalid, in cases such as:

- missing governance files
- malformed governance objects
- invalid trust root
- unknown signer
- revoked signer
- broken rotation continuity
- manifest hash mismatch
- inconsistent governance version
- signature valid but signer unauthorized

A verifier should distinguish clearly between:

- cryptographic failure
- governance failure
- policy failure
- data absence

These are not the same class of error.

---

## 13. Relationship to TUF

ISC Core governance is best understood as **portable, TUF-inspired governance**.

Similarities to TUF include:

- trust root concept
- signer authorization
- revocation support
- rotation support
- policy-aware verification

Differences from TUF include:

- no required metadata server
- no assumption of online metadata refresh
- governance may travel with the evidence pack
- verification is centered on a sealed release evidence object, not repository update metadata

In short:

> TUF distributes trust through repository metadata.  
> ISC Core carries trust with the pack.

---

## 14. Relationship to Sigstore

ISC Core governance differs from Sigstore-style trust in several ways.

ISC Core does not require:

- certificate-based signer identity
- OIDC identity proofs
- transparency log access during verification
- hosted trust services

Instead, ISC Core focuses on:

- portable signer authorization
- offline governance evaluation
- pack-local trust context

This makes ISC Core less identity-centric and more pack-centric.

---

## 15. Security Considerations

Governance improves verification quality, but does not eliminate all risk.

ISC Core governance does **not** guarantee:

- that a signer was honest
- that the build environment was uncompromised
- that the trust root was distributed safely
- that local verifier policy is correct
- that all future revocations are known offline

Governance only allows the verifier to reason about authorization using the governance state available to it.

That is powerful, but bounded.

---

## 16. Recommended Implementation Guidance

Implementations should:

- use stable signer identifiers
- canonicalize governance files before hashing
- separate cryptographic validity from policy validity
- display governance failures clearly
- version governance objects explicitly
- preserve historical governance material where auditability matters
- make revocation evaluation mode visible to the user

Implementations should avoid:

- hidden trust roots
- implicit online dependencies
- unverifiable signer aliases
- silent revocation bypass
- mixing identity claims with signer authorization unless explicitly modeled

---

## 17. Summary

ISC Core governance defines how signer authorization is represented and evaluated in a portable verification system.

It is:

- inspired by TUF
- simpler than certificate-based trust systems
- independent of mandatory metadata servers
- designed for offline, durable verification

Its central principle is simple:

> authorization state must remain verifiable even when the service that produced the pack is gone.
