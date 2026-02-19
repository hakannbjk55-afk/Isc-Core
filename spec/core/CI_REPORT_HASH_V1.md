# CI Report Hash V1 (Deterministic)

## Purpose
Define a verifier-independent, deterministic SHA-256 digest for the CI report payload.

## Input
A JSON object (the deterministic CI report).

## Canonical JSON serialization
The digest MUST be computed over the UTF-8 bytes of the JSON produced with:

- ensure_ascii: false
- sort_keys: true
- separators: (",", ":")

This exactly matches Python:
json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

## Hash algorithm
SHA-256 over the canonical JSON bytes.

## Output format
Lowercase hexadecimal string, 64 characters.

## Determinism rule
The deterministic report MUST NOT contain runtime-varying fields such as timestamps.
Runtime metadata MUST be stored separately and MAY embed this deterministic digest.
