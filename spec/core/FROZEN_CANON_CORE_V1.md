# ISC Canonical Core v1 — FROZEN

**Status:** FROZEN  
**Date:** 2026-02-21  
**Core Version:** 11.0.0  

## Declaration

ISC Canonical Core v1 is hereby declared FROZEN.

The canonical byte behavior defined by this version MUST NOT change.
Any behavior change that can affect canonical output bytes MUST be released as a new MAJOR version (v2+).

## Frozen surface (normative)

The following are normatively frozen:

- Canonicalization profile and output bytes
- Strict JSON object parsing: duplicate object keys MUST be rejected (HARD FAIL)
- Input encoding: UTF-8 bytes are authoritative; implementations MUST NOT perform Unicode normalization (NFC/NFKC/etc.)
- Limits: MAX_DEPTH = 64; exceeding MUST fail with error code `DEPTH_LIMIT_EXCEEDED`
- Error signaling: errors MUST include a stable error code from `ERROR_REGISTRY_V1`
- Negative zero policy: `-0` MUST canonicalize as `0`
- Conformance suite: `test_vectors/vector_0001..vector_0014` with `test_vectors/manifest.json` sha256 pins

## Not frozen (out of scope)

The following are explicitly NOT frozen by this document:

- Governance documents and processes
- Evidence pack tooling and packaging scripts
- Verifier orchestration and CI policy glue
- Upper layers (signing, sealing, key governance, adapters)

## Conformance requirements

A conforming v1 implementation MUST:

- Match canonical outputs for all PASS vectors in the pinned conformance suite
- Reject duplicate keys (HARD FAIL)
- Enforce MAX_DEPTH = 64 (DEPTH_LIMIT_EXCEEDED)
- Emit a stable error code for failures (message text MAY vary)
