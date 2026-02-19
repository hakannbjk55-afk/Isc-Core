# Verifier Bundle v1

## Purpose
A Verifier Bundle is a frozen, offline-capable verification toolkit that allows any third party
to validate an Evidence Pack without cloning the original repository or trusting the producer.

The bundle MUST be self-contained and MUST run without network access.

## Bundle contents (required)
The Verifier Bundle v1 MUST include the following files:

- tools/verify_evidence_pack_v1.sh
- tools/ci_report_hash_v1.py
- spec/core/CI_REPORT_HASH_V1.md
- spec/EVIDENCE_PACK.md
- spec/core/VERSION

## Determinism
The bundle itself MUST be reproducible:
rebuilding the bundle from the same repository state MUST produce identical bytes.

## Bundle identity
The bundle identity MUST be defined by:
- bundle tarball SHA-256
- a SHA256SUMS file inside the bundle

## Verification contract
Given:
- verifier_bundle_v1.tar
- evidence_pack_v1.tar
- evidence_pack_v1.sha256

A verifier MUST be able to run:
- verify_evidence_pack_v1.sh evidence_pack_v1.tar evidence_pack_v1.sha256

and obtain a deterministic PASS/FAIL result.

## Offline guarantee
No part of verification may require:
- GitHub
- git clone
- remote APIs
- online timestamps
