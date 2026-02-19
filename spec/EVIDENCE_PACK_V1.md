# Evidence Pack v1

This document defines a deterministic, portable evidence package format.

## Goals
- Platform-independent verification
- Deterministic packaging (same inputs -> same bytes -> same hash)
- Minimal surface area

## Pack contents (required)
- artifacts/ci_report.json
- spec/core/VERSION
- test_vectors/manifest.json
- test_vectors/*.json
- tools/ci_policy.sh (policy snapshot)
- tools/version_gate.sh
- tools/phi_tripwire.sh

## Deterministic packaging rules
- Archive format: tar
- File order: lexicographic by path
- Metadata normalization:
  - uid=0, gid=0
  - uname="", gname=""
  - mtime=0
  - mode preserved from working tree
- Compression: none (plain .tar)

## Output
- artifacts/evidence_pack_v1.tar
- artifacts/evidence_pack_v1.sha256 (sha256 of the tar bytes)

## Expected layout (offline verification)

The verifier expects the following exact layout:

- artifacts/evidence_pack_v1.tar
- artifacts/evidence_pack_v1.sha256

The SHA256 file MUST reference the tar file using the exact path:

artifacts/evidence_pack_v1.tar

## Example verification (offline)

From the directory root:

sha256sum -c artifacts/evidence_pack_v1.sha256

## Verification script

Use:

tools/verify_evidence_pack_v1.sh

