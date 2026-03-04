# ISC Evidence Pack V2 — Core Specification (Draft)

## 1. Overview

ISC Evidence Pack V2 defines a portable, cryptographically verifiable proof format for digital events.

An evidence pack represents a single event (e.g., build, test, release, deploy, inference) together with the cryptographic proof required to verify:

- event integrity
- artifact lineage
- governance authority
- timestamp anchoring

Evidence packs are designed to be portable, independently verifiable, resistant to tampering, and suitable for audit and compliance workflows.

## 2. Hash Model

Three-layer hash model:

### meta_hash
meta_hash = SHA256(canonical(meta_json))
Includes: event_type, parents, inputs, outputs, source, governance references.

### content_hash
content_hash = SHA256(canonical(content_manifest))
Content manifest MUST include every file except itself.

### pack_hash
pack_hash = SHA256(meta_hash || content_hash)
Only pack_hash is anchored to external systems.

## 3. Evidence Pack Structure
evidence_pack_v2.tar
/artifacts
ci_report.json
signatures/
/governance
allowed_signers
rotation_records
revocation_records
/time_layer
attestation.json
content_manifest.sha256
Verification MUST NOT rely on TAR byte-level hashing.

## 4. Metadata Schema

```json
{
  "version": "2",
  "event_type": "release",
  "pack_hash": "sha256:...",
  "meta_hash": "sha256:...",
  "content_hash": "sha256:...",
  "parents": [
    {
      "pack_hash": "sha256:...",
      "event": "build"
    }
  ],
  "inputs": ["sha256:..."],
  "outputs": ["sha256:..."],
  "source": {
    "repo": "git://example/repo",
    "commit": "abc123"
  }
}
5. Parent Relationships
build → test → package → release
release.parents = [package_pack_hash]
package.parents = [test_pack_hash]
test.parents = [build_pack_hash]
6. Artifact Lineage Rule
For each parent:
parent.outputs ⊆ child.inputs
If this condition fails, lineage verification MUST fail.
7. Verification Algorithm
Step 1: Recompute meta_hash
Step 2: Recompute content_hash
Step 3: Recompute pack_hash
Step 4: Timestamp verification (pack_hash on-chain)
Step 5: Governance verification (signer allowed, not revoked)
Step 6: Lineage verification (parent.outputs ⊆ child.inputs)
8. Security Model
Guarantee
Mechanism
Integrity
content_hash
Semantic Integrity
meta_hash
Pack Identity
pack_hash
Timestamp Proof
on-chain anchor
Governance
allowed_signers + revocation
Pipeline Lineage
parent.outputs ⊆ child.inputs
9. Design Goals
Portable cryptographic evidence
Audit-ready proof bundles
Independent verification
Minimal external dependencies
Deterministic verification
Small pack size (≈30KB)
10. Non-Goals
Does not replace CI systems, provenance frameworks, or artifact registries. Focuses only on portable cryptographic proof of digital events.
11. Summary
Evidence Pack V2 proves: This event occurred, under this governance, producing these artifacts, derived from these inputs, and existed at this time.
All claims are cryptographically verifiable using the evidence pack alone together with the timestamp anchor.
