# ISC Core Security Model

## 1. Purpose

ISC Core exists to make software release evidence portable, independently verifiable, and durable over time.

Its purpose is not to prove that a build environment was honest.
Its purpose is to prove that an evidence pack, once produced, can be verified later without depending on a server, SaaS platform, hosted log, or external API.

In practical terms, ISC Core is designed so that a verifier can take a single pack, run `isc_verify`, and determine whether the pack is structurally valid, cryptographically intact, and signed under the expected governance context.

---

## 2. Goals

ISC Core is designed to provide the following guarantees:

1. **Integrity of the evidence pack**  
   If the pack contents are modified after sealing, verification must fail.

2. **Authenticity of signatures**  
   The verifier must be able to determine whether the pack was signed by authorized keys.

3. **Portable verification**  
   Verification must work offline, without requiring a hosted transparency log, online identity provider, or platform account.

4. **Governance-aware verification**  
   Verification must incorporate governance state, including allowed signers, revocation state, and key rotation rules where present.

5. **Provenance binding**  
   The pack may bind an artifact to contextual metadata such as repository, commit, build event, builder identity, lineage, and related release metadata.

6. **Durable audit evidence**  
   The pack should remain useful as evidence even if the original CI system, Git hosting provider, company account, or BuildSeal service no longer exists.

---

## 3. Non-Goals

ISC Core explicitly does **not** attempt to provide the following:

1. **Proof that the build environment was honest**  
   ISC Core does not prove that a builder, CI runner, or signing environment was uncompromised.

2. **Proof that the artifact was deterministically built from source**  
   Unless combined with external reproducibility systems, ISC Core does not prove reproducible builds.

3. **Detection of malicious source code**  
   ISC Core does not analyze code for malware, backdoors, or insecure logic.

4. **Prevention of insider abuse**  
   If an attacker controls an authorized signing key or compromised builder with signing capability, they may produce a cryptographically valid but misleading pack.

5. **Universal timestamp truth without external anchoring**  
   Offline verification alone does not prove that a pack existed at a claimed real-world time. That requires an external timestamping or anchoring mechanism.

6. **Replacement for transparency logs, secure builders, or trusted execution**  
   ISC Core can integrate with these systems, but it does not replace them.

---

## 4. Trust Assumptions

ISC Core relies on a small set of explicit trust assumptions.

Verification results are meaningful only if these assumptions hold.

### 4.1 Trusted verification binary
The verifier must trust the `isc_verify` binary or independently inspect/rebuild it from source.

### 4.2 Trusted public keys or governance root
The verifier must obtain the correct trust root: public keys, governance policy, or governance state used to evaluate signatures.

### 4.3 Sound cryptographic primitives
The underlying hash and signature algorithms must remain computationally secure for the intended verification horizon.

### 4.4 Correct pack specification
Pack producers and verifiers must interpret the pack format in the same canonical way.

### 4.5 Honest pack creation moment is not assumed
ISC Core does **not** assume the build environment was honest. This is a limitation, not a guarantee.

---

## 5. Threat Model

ISC Core is designed to resist a specific class of threats.

### 5.1 Threats ISC Core addresses

ISC Core is intended to detect or mitigate:

- Modification of artifact metadata after pack creation
- Tampering with signatures, lineage, or governance references inside the pack
- Post-hoc alteration of release evidence
- Loss of hosted verification infrastructure
- Inability to verify a release after CI logs, accounts, or dashboards disappear
- Unauthorized signatures from keys not permitted by governance state
- Use of revoked keys, where revocation data is present and checked

### 5.2 Threats ISC Core does not fully address

ISC Core does not fully defend against:

- A malicious or compromised build runner
- A malicious actor with access to an authorized signing key
- False provenance generated at pack creation time
- A compromised source repository before sealing
- Weak operational key management
- Social engineering around trust root distribution
- Future cryptographic breaks unless migrated forward

---

## 6. Verification Guarantees

When `isc_verify` returns success, ISC Core provides a bounded set of guarantees.

### 6.1 Offline guarantees

A successful offline verification means, at minimum:

- The pack structure is valid
- Required files and metadata are present
- The referenced hashes are consistent
- The content has not been modified after sealing
- The signatures validate against the expected trust root
- Governance rules embedded in the verification context are satisfied
- Provenance metadata inside the pack is internally consistent

### 6.2 What offline verification does **not** guarantee

A successful offline verification does **not** mean:

- the build system was uncompromised
- the claimed source commit was actually built
- the artifact is safe
- the code is benign
- the timestamp is globally true
- the builder was honest

### 6.3 Optional anchored guarantees

If external anchoring or timestamp verification is enabled and succeeds, ISC Core may additionally support claims such as:

- the pack hash was committed to an external ledger
- the pack existed no later than the anchor time
- the evidence existed independently of the BuildSeal service

These guarantees depend on the security and availability of the external anchoring system.

---

## 7. Known Limitations

This section documents the most important limitation clearly.

### 7.1 Pack creation is the weakest trust boundary
ISC Core can strongly verify a pack **after** it exists.
It cannot fully prove that the pack was honestly created.

If a compromised builder produces:

- a false commit reference,
- a misleading artifact hash,
- or manipulated provenance,

and signs it with a currently authorized key,
the verifier may still return `VERIFIED`.

This is not a bug in ISC Core alone.
It is a general limitation shared by modern supply-chain evidence systems unless combined with stronger build trust mechanisms.

### 7.2 Timestamp truth requires external evidence
A local signature can prove authorship and integrity, but not independent real-world existence at a claimed time.
That requires external timestamping or anchoring.

### 7.3 Long-term verification requires migration planning
As algorithms age, governance state evolves, or trust roots rotate, long-term verification may require pack versioning, trust-root migration, or cryptographic refresh.

### 7.4 Governance quality matters
ISC Core can verify under governance rules, but cannot rescue a poorly designed governance model.
Weak signer selection or weak revocation hygiene weakens the total system.

---

## 8. Security Philosophy

ISC Core is intentionally conservative in what it claims.

It does not claim to prove absolute software honesty.
It does not claim to solve the trusted build problem.
It does not claim to eliminate all supply-chain risk.

Instead, ISC Core claims something narrower and more durable:

> A release evidence pack can be made portable, tamper-evident, governance-aware, and independently verifiable.

That narrower claim is deliberate.
It is also the foundation that allows long-lived audit evidence to exist without dependence on a vendor service.

---

## 9. Relationship to Other Systems

ISC Core is compatible in spirit with supply-chain and provenance systems such as signed attestations, transparency logs, and policy frameworks.

Its primary distinction is architectural:

- many systems are **log-centric**
- ISC Core is **pack-centric**

Many systems assume verification is performed against a live service.
ISC Core assumes the service may disappear, while the evidence must remain verifiable.

In that sense, ISC Core is best understood as a portable digital evidence model for software releases.

---

## 10. Recommended Layering

ISC Core is strongest when combined with additional controls:

- hardened CI runners
- isolated signing infrastructure
- short-lived signing keys
- reproducible builds
- external timestamping / blockchain anchoring
- transparency logs
- policy enforcement
- artifact retention and archival strategy

ISC Core should be treated as one layer in a broader release integrity stack, not the only layer.

---

## 11. Summary

ISC Core guarantees the integrity and verifiability of a sealed evidence pack.

It does not guarantee the honesty of the build environment that created that pack.

That distinction is the core security boundary of the system.

By making this boundary explicit, ISC Core aims to be more useful, more portable, and more honest than systems that imply stronger guarantees than they can actually provide.
