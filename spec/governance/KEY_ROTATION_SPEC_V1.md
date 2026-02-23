# KEY_ROTATION_SPEC_V1

Status: Active  
Applies to: ISC Core v1.0.0-isc-core-frozen  

---

## 1. Governance Model

Current quorum:
quorum: 1-of-1

This reflects the current operational reality: a single active signer.

Planned migration path:
migration_path: 2-of-3

Future versions may expand quorum requirements without breaking backward verification.

---

## 2. Rotation Triggers

Key rotation may be triggered by:

### A) Time-Based Trigger
- max_key_age_days: 365
- rotate_before_days: 14
When max age is exceeded, rotation_due = true.

### B) Event-Based Trigger
Emergency rotation MUST occur if:
- Signing key compromise is suspected or confirmed
- Signing device loss or theft occurs
- Unauthorized signature is detected
- Governance policy is altered unexpectedly

This sets rotation_emergency = true.

### C) Governance Trigger
Rotation is only considered valid when confirmed by quorum approval.

In v1:
quorum_required = 1

---

## 3. Rotation Execution Artifact

A rotation event MUST produce:

rotation_commit.json

Required fields:

- previous_key_id
- new_key_id
- rotation_reason (time | emergency | governance)
- approved_by
- approved_at_utc
- policy_version
- rotation_hash

The rotation_commit.json MUST be signed by the active quorum.

---

## 4. Revocation Model

Upon successful rotation:

- previous_key_id status = revoked
- revocation_record.json MUST be generated
- revocation_record MUST be included in subsequent Evidence Pack

Revocation does NOT invalidate historical signatures.
It prevents future acceptance of revoked keys.

---

## 5. Verification Rules

Verification engines MUST:

- Accept historical attestations signed before revocation timestamp
- Reject attestations signed after revocation timestamp using revoked key
- Validate rotation_commit signature against quorum policy

---

## 6. Security Boundaries

This spec defines governance mechanics only.

It does NOT:
- Define legal identity binding
- Provide external transparency anchoring
- Prevent insider misuse before detection

---

Version: KEY_ROTATION_SPEC_V1
Linked Release: v1.0.0-isc-core-frozen

---

## 7. Rotation Commit Format (Normative)

A key rotation MUST produce a file named:

rotation_commit.json

The file MUST conform to the following canonical structure:

{
  "version": "KEY_ROTATION_V1",
  "namespace": "isc-core.key_rotation_v1",
  "rotation_id": "",
  "rotation_type": "scheduled | emergency | governance",
  "policy_version": "1-of-1",

  "created_utc": "",
  "effective_timestamp": "",

  "old_key_fingerprint": "",
  "new_key_fingerprint": "",
  "key_scheme": "ssh-ed25519",

  "rotation_reason": "",

  "repo_commit": "",
  "state_hash": "",

  "prev_rotation_hash": null,
  "rotation_commit_hash": "",

  "quorum_signatures": [
    {
      "signer_id": "",
      "key_fingerprint": "",
      "sig_alg": "ssh-ed25519",
      "signature_file": "",
      "sig_sha256": ""
    }
  ]
}

### Canonicalization Rules

- JSON MUST be canonical (deterministic field order).
- All timestamps MUST be RFC3339 UTC (ending with Z).
- rotation_commit_hash MUST be computed over canonical JSON (excluding quorum_signatures).
- quorum_signatures MUST sign rotation_commit_hash.
- Namespace for signature verification MUST be:
  isc-core.key_rotation_v1

### Validation Requirements

Verification engines MUST:

- Validate canonical structure
- Validate rotation_commit_hash integrity
- Validate quorum threshold
- Validate signature namespace binding
- Validate policy_version consistency

