# KEY_REGISTRY_V1

Status: DRAFT (normative)
Scope: Defines the authoritative public-key registry snapshot embedded in an Evidence Pack.
Security objective: Offline, third-party verifiable selection of the correct public key for PACK_SEAL_V1 verification.

---

## 1. Terminology (normative)

- **Registry**: A JSON document (`key_registry.json`) embedded inside the Evidence Pack that lists public keys and their governance metadata.
- **Key entry**: One object in the registry representing a single public key and its lifecycle.
- **Active key**: A key eligible for signing at a given time according to the selection rule.
- **Verifier**: A deterministic program that validates the pack hash, selects the correct key, and verifies the signature.

---

## 2. Files and locations (normative)

The Evidence Pack MUST include:

- `artifacts/key_registry.json`
- `artifacts/key_registry.json.sha256`

The SHA256 file MUST be computed over the exact bytes of `artifacts/key_registry.json`.

---

## 3. Registry canonicalization and parsing (normative)

3.1 JSON parsing MUST be strict:

- Duplicate keys MUST be rejected.
- Non-UTF-8 input MUST be rejected.
- Surrogate code points MUST be rejected.

3.2 Registry JSON MUST be canonicalized under the repository's canonicalization rules:

- `canonicalization_rule_version` MUST be included in the registry document.
- Verifiers MUST apply the corresponding canonicalization rules when computing hashes for governance checks, but signature verification uses the raw `pack_hash` defined by the Evidence Pack authoritative byte model.

---

## 4. Key identifiers (normative)

4.1 `key_id` MUST be deterministically derived as:

- `key_id = "sha256:" + hex( SHA256( public_key_bytes ) )`

Where:

- `public_key_bytes` are the raw 32-byte Ed25519 public key (NOT base64 text, NOT JSON string bytes).
- The SHA256 digest MUST be lowercase hex.

4.2 `public_key` MUST be encoded as base64 without whitespace.
Decoding MUST yield exactly 32 bytes for Ed25519.

---

## 5. Key use (normative)

`key_use` MUST be the fixed enum:

- `"PACK_SEAL_V1"`

No other uses are permitted in KEY_REGISTRY_V1.

---

## 6. Time semantics (normative)

6.1 Time fields MUST be RFC3339 timestamps in UTC with `Z` suffix (e.g., `2026-02-20T21:00:00Z`).

6.2 Fields:

- `not_before` (optional): If present, verification MUST FAIL with `KEY_NOT_YET_VALID` when `verification_time < not_before`.
- `not_after` (optional): If present, verification MUST FAIL with `KEY_EXPIRED` when `verification_time > not_after`.
- `revoked_at` (optional): If present, verification MUST FAIL with `KEY_REVOKED` when `verification_time >= revoked_at`.

6.3 `verification_time` source:

- The verifier MUST use the Evidence Pack's authoritative time reference if available (e.g., a timestamp token time).
- If no authoritative time exists, `verification_time` MUST be derived from the pack's embedded metadata field `pack_created_at` (defined in the Evidence Pack spec). If that is absent, verification MUST FAIL with `TIME_SOURCE_MISSING`.

---

## 7. Rotation and key selection (normative)

7.1 Registry MUST contain `active_selection_rule` with a fixed value:

- `"LATEST_NOT_REVOKED_BY_NOT_BEFORE"`

7.2 Selection algorithm:

Given all keys with `key_use == "PACK_SEAL_V1"`:

1) Filter out keys that are invalid at `verification_time` based on not_before/not_after/revoked_at.
2) From remaining keys, select the key with the greatest `not_before`.
   - If a key has no `not_before`, treat it as the lowest possible time.
3) If multiple keys tie, select the one with lexicographically smallest `key_id`.
4) If no keys remain, verification MUST FAIL with `NO_VALID_KEY`.

7.3 A key MAY be marked `is_signing_preferred=true`. This flag MUST NOT override the deterministic selection algorithm.

---

## 8. Revocation semantics (normative)

8.1 `revocation_reason_code` MUST be one of:

- `"KEY_COMPROMISE"`
- `"OPERATOR_ERROR"`
- `"POLICY_ROTATION"`
- `"CRYPTO_MIGRATION"`
- `"UNKNOWN"`

8.2 If `revoked_at` is present, `revocation_reason_code` MUST be present.

---

## 9. Registry schema (normative)

The registry JSON MUST conform to:

### 9.1 Top-level object

Required fields:
- `schema` (string): MUST equal `"KEY_REGISTRY_V1"`
- `schema_version` (string): MUST equal `"1"`
- `canonicalization_rule_version` (string)
- `active_selection_rule` (string): MUST equal `"LATEST_NOT_REVOKED_BY_NOT_BEFORE"`
- `keys` (array of key entries)

Optional fields:
- `registry_created_at` (RFC3339 UTC)
- `registry_comment` (string)

### 9.2 Key entry object

Required fields:
- `key_id` (string): `sha256:<64 hex>`
- `key_use` (string): MUST equal `"PACK_SEAL_V1"`
- `public_key` (string): base64 of 32 bytes
- `created_at` (RFC3339 UTC)

Optional fields:
- `not_before` (RFC3339 UTC)
- `not_after` (RFC3339 UTC)
- `revoked_at` (RFC3339 UTC)
- `revocation_reason_code` (enum)
- `operator` (string)
- `comment` (string)
- `is_signing_preferred` (boolean)

---

## 10. Deterministic failure codes (normative)

Verifier MUST emit one of:

- `OK`
- `FAIL:REGISTRY_HASH_MISMATCH`
- `FAIL:REGISTRY_PARSE_ERROR`
- `FAIL:TIME_SOURCE_MISSING`
- `FAIL:NO_VALID_KEY`
- `FAIL:KEY_NOT_YET_VALID`
- `FAIL:KEY_EXPIRED`
- `FAIL:KEY_REVOKED`
- `FAIL:PUBLIC_KEY_DECODE_ERROR`
- `FAIL:SIGNATURE_INVALID`
- `FAIL:PACK_HASH_ERROR`

---

## 11. Example (non-normative)

```json
{
  "schema": "KEY_REGISTRY_V1",
  "schema_version": "1",
  "canonicalization_rule_version": "CANON_V1",
  "active_selection_rule": "LATEST_NOT_REVOKED_BY_NOT_BEFORE",
  "registry_created_at": "2026-02-20T21:00:00Z",
  "keys": [
    {
      "key_id": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "key_use": "PACK_SEAL_V1",
      "public_key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
      "created_at": "2026-02-20T21:00:00Z",
      "not_before": "2026-02-20T21:00:00Z"
    }
  ]
}
git add spec/core/KEY_REGISTRY_V1.md
git commit -m "spec(core): add KEY_REGISTRY_V1 normative governance model"
git push
