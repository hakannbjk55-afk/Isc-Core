# ISC Core
![CI](https://github.com/hakannbjk55-afk/Isc-Core/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/hakannbjk55-afk/Isc-Core)
Solves: verifiable CI integrity, signed governance lifecycle, and offline release validation.

ISC Core is a deterministic CI verification engine that binds build artifacts to signed governance and time-anchored Evidence Packs.

It enforces deterministic hashing, signed governance lifecycle, artifact binding, and offline-verifiable release attestations.

ISC Core defines a strict integrity boundary.

## Quick Start (60-Second Verification)

git clone git@github.com:hakannbjk55-afk/Isc-Core.git
cd ISC-Core
python tools/verifier.py examples/sample_evidence_pack_v2.tar

Expected result:

Archive SHA256: OK
Signature: VALID
Governance rotation: VALID
Governance revocation: VALID
Artifact binding: VALID
CI report hash: MATCH
VERDICT: TRUSTED

Verification works fully offline.

## Latest Stable Release

https://github.com/hakannbjk55-afk/Isc-Core/releases/tag/v1.7.0-hardening-baseline
