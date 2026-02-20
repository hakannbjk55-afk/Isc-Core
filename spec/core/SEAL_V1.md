# SEAL_V1

Status: DRAFT (normative)
Scope: Defines pack-level cryptographic sealing for Evidence Pack v1 using Ed25519.

---

## 1. Goals (normative)

- Produce a deterministic, offline-verifiable seal over an Evidence Pack.
- Bind the seal to a specific key registry snapshot (KEY_REGISTRY_V1).
- Avoid circular hashing (signature file MUST NOT be within the hashed bytes).

---

## 2. Files and locations (normative)

Evidence Pack v1 MUST include:

- `artifacts/pack_signature.json`

Optionally, distributors MAY provide:

- `artifacts/evidence_pack_v1.tar.sig` (detached signature over `pack_hash`)

---

## 3. Authoritative pack hash model (normative)

3.1 `pack_hash` MUST be computed over the Evidence Pack tar bytes under the Evidence Pack v1 deterministic packaging rules, with the following exclusion:

- The file `artifacts/pack_signature.json` MUST be treated as excluded from the `pack_hash` computation.

3.2 Exclusion rule MUST be deterministic:

- The pack hash is computed over a virtual tar stream that is identical to the produced tar, except that the entry at path `artifacts/pack_signature.json` is omitted.
- All other files MUST remain unchanged.

3.3 Hash algorithm:

- `hash_alg` MUST be `"sha256"` for SEAL_V1.

---

## 4. Key registry binding (normative)

4.1 The seal MUST bind to the embedded key registry snapshot:

- `registry_path` MUST equal `artifacts/key_registry.json`
- `registry_hash` MUST be `sha256` over the exact bytes of `artifacts/key_registry.json`
- `registry_schema` MUST equal `"KEY_REGISTRY_V1"`
- `registry_schema_version` MUST equal `"1"`

4.2 The verifier MUST FAIL if:

- `registry_hash` does not match the embedded registry bytes, or
- the registry does not conform to KEY_REGISTRY_V1 parsing requirements.

---

## 5. Seal algorithm (normative)

5.1 `seal_alg` MUST be `"ed25519"`.

5.2 Signature input:

- The signature MUST be computed over the ASCII bytes of the following canonical message:

`"SEAL_V1|" + pack_hash`

Where `pack_hash` is the lowercase hex digest (64 hex chars) of SHA256.

Example message:
`SEAL_V1|264b6deb0aa30cce4bc78f1ece2c8f64b62a836709b888fc8f71235e7b433975`

5.3 Signature encoding:

- `signature` MUST be base64 (no whitespace) of the raw Ed25519 signature bytes (64 bytes).

---

## 6. pack_signature.json schema (normative)

Top-level object MUST include:

Required:
- `schema`: MUST be `"PACK_SIGNATURE_V1"`
- `schema_version`: MUST be `"1"`
- `created_at`: RFC3339 UTC timestamp (Z)
- `hash_alg`: MUST be `"sha256"`
- `pack_hash`: lowercase hex SHA256 digest (64 hex)
- `seal_alg`: MUST be `"ed25519"`
- `key_use`: MUST be `"PACK_SEAL_V1"`
- `key_id`: MUST match KEY_REGISTRY_V1 `key_id` for the selected public key
- `registry_path`: MUST be `"artifacts/key_registry.json"`
- `registry_schema`: MUST be `"KEY_REGISTRY_V1"`
- `registry_schema_version`: MUST be `"1"`
- `registry_hash`: lowercase hex SHA256 digest (64 hex) over exact registry bytes
- `canonicalization_rule_version`: string (copied from registry)
- `signature`: base64 Ed25519 signature of the SEAL_V1 message

Optional:
- `context_code`: string (deterministic if used; otherwise omit)
- `comment`: string

JSON parsing MUST be strict:
- Duplicate keys MUST be rejected.
- Non-UTF-8 input MUST be rejected.
- Surrogates MUST be rejected.

---

## 7. Verification algorithm (normative)

Given an Evidence Pack tar:

1) Extract `artifacts/key_registry.json` and `artifacts/pack_signature.json`.
2) Compute `registry_hash` over exact registry bytes; compare to `pack_signature.json.registry_hash`.
3) Parse registry under KEY_REGISTRY_V1. Determine `verification_time` per KEY_REGISTRY_V1 rules.
4) Select the public key deterministically per KEY_REGISTRY_V1 selection rule.
   - The selected key's `key_id` MUST match `pack_signature.json.key_id`.
5) Compute `pack_hash` using the exclusion rule (omit `artifacts/pack_signature.json`).
   - Compare to `pack_signature.json.pack_hash`.
6) Verify Ed25519 signature over message `SEAL_V1|<pack_hash>`.
7) Output MUST be deterministic:
   - `OK` if all checks pass
   - otherwise `FAIL:<reason_code>`

Reason codes:
- `REGISTRY_HASH_MISMATCH`
- `REGISTRY_PARSE_ERROR`
- `PACK_SIGNATURE_PARSE_ERROR`
- `PACK_HASH_MISMATCH`
- `NO_VALID_KEY`
- `KEY_NOT_YET_VALID`
- `KEY_EXPIRED`
- `KEY_REVOKED`
- `SIGNATURE_INVALID`
- `TIME_SOURCE_MISSING`

---

## 8. Detached signature (optional, non-normative)

If `evidence_pack_v1.tar.sig` is provided, it MUST be the raw Ed25519 signature over the same canonical message `SEAL_V1|<pack_hash>`.
This file is distribution-only and MUST NOT replace `artifacts/pack_signature.json` as the source of truth.

