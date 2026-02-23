# REVOCATION_RECORD_SPEC_V1

Status: Active
Applies to: ISC Core v1.0.0-isc-core-frozen

This spec defines the revocation record format and verifier rules for key revocation.

---

## 1. Purpose

A revocation record declares that a signing key is no longer valid starting at a specific effective time.

Authoritative time source:
- effective_timestamp is authoritative ONLY from rotation_commit.json.
- revocation_record.json MUST NOT define its own independent timestamp source.

---

## 2. File: revocation_record.json (Normative)

### 2.1 Schema (JSON)

{
  "version": "KEY_REVOCATION_V1",
  "revoked_key_fingerprint": "",
  "revocation_reason": "",
  "rotation_commit_ref": "",
  "effective_timestamp": ""
}

### 2.2 Field Rules

- version MUST equal KEY_REVOCATION_V1.
- revoked_key_fingerprint MUST use canonical fingerprint format.
- rotation_commit_ref MUST match rotation_commit.json.rotation_id.
- effective_timestamp MUST equal rotation_commit.json.effective_timestamp.
- effective_timestamp MUST be RFC3339 UTC (ending with Z).

---

## 3. Canonicalization

- JSON MUST be canonical and deterministic.
- No extra fields are allowed.

---

## 4. Verifier Rules (Normative)

A verifier MUST:

1. Validate that rotation_commit_ref exists.
2. Validate effective_timestamp matches rotation_commit.json.
3. Reject signatures made by revoked_key_fingerprint at or after effective_timestamp.
4. Accept signatures made before effective_timestamp if valid under prior policy.

Failure of any rule MUST result in verification rejection.

---

Version: KEY_REVOCATION_SPEC_V1
