# ISC Core

ISC Core is a reproducible verification engine that produces cryptographically bound Evidence Packs from CI pipelines.

It enforces deterministic hashing, signed governance lifecycle, artifact binding, and offline-verifiable release attestations.

ISC Core defines a strict integrity boundary.

## Quick Start (60-Second Verification)

git clone <repo-url>
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
