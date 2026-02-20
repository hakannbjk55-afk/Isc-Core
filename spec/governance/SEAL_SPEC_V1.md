# ICS Seal Specification v1

## Purpose

Seal layer cryptographically binds:
- Evidence pack hash
- Seal time (UTC)
- Issuer identity

This layer does NOT modify canonical bytes.
It operates strictly after evidence pack generation.

---

## Seal Payload Structure

Signature payload MUST be constructed as:

ICS_SIG_V1\0<pack_sha256>\0<seal_time_utc>\0<issuer>

Where:

- pack_sha256: SHA256 of evidence_pack_v1.tar
- seal_time_utc: RFC3339 UTC timestamp (second precision)
- issuer: stable identifier of signing entity

---

## Seal JSON Structure

seal.json MUST contain:

{
  "pack_sha256": "<hex>",
  "seal_time_utc": "<RFC3339 UTC>",
  "issuer": "<string>",
  "sig_alg": "ed25519",
  "signature": "<base64>"
}

---

## Security Properties

- Canonical bytes remain unchanged.
- Seal time is bound to signature.
- Backdating without private key is not possible.
- Determinism layer and seal layer are separated.

---

## External Time Anchoring (Optional)

Seal MAY include:

- RFC3161 timestamp token
- Public append-only log anchor
- Blockchain reference

This provides stronger temporal guarantees but is not required for v1.

