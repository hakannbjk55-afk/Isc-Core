# BuildSeal

BuildSeal is a portable software integrity verification system.

It allows you to seal build artifacts into a cryptographically signed evidence pack,
and verify them later without trusting the original server, repository, or BuildSeal itself.

The goal of BuildSeal is simple:

Anyone should be able to verify what was built, when it was built, and by whom —
using only the artifact and the evidence pack.


## Quick start

Download verifier:

https://github.com/hakannbjk55-afk/Isc-Core/releases/download/v0.2.0/isc_verify

Make it executable:
chmod +x isc_verify
Download example evidence pack:
https://verify.buildseal.io/release/seal_1772887285176_trxc9ufi
Verify:
./isc_verify evidence_pack.tar
Result:

Genuine  -> artifact matches the sealed build
Modified -> artifact was changed


## Overview

BuildSeal produces a self-contained proof bundle that includes:

- Artifact hash
- Signature
- Build metadata (repository, commit, timestamp)
- Governance key
- Verification policy

Verification can be done:

- offline
- without API calls
- without a central registry
- without trusting BuildSeal


## Use cases

- software supply chain verification
- release integrity validation
- audit evidence packs
- reproducible build workflows
- security-sensitive environments


## Design Principles

No central trust required.
Verification must work offline.
Proof must be portable.
Artifacts must be self-verifiable.
Failure must be obvious.

If verification requires trusting a server, it is not verification.
If proof cannot be moved, it is not proof.
If integrity cannot be checked locally, it is not integrity.


## What BuildSeal is NOT

BuildSeal is not a CI system.
BuildSeal is not a package registry.
BuildSeal is not a signing server.
BuildSeal is not a blockchain project.

BuildSeal is a verification tool.


## ISC Engine

BuildSeal uses the ISC (Integrity Seal Chain) engine.

ISC provides:

- Ed25519 signatures
- Deterministic sealing
- Portable evidence packs
- Policy-based verification
- Offline trust model

Verification output is binary: Genuine or Modified.


## Independent verification

You can verify without trusting BuildSeal.

Download verifier:

https://github.com/hakannbjk55-afk/Isc-Core/releases/download/v0.2.0/isc_verify

Example:
curl -L https://github.com/hakannbjk55-afk/Isc-Core/releases/download/v0.2.0/isc_verify -o isc_verify
chmod +x isc_verify
./isc_verify evidence_pack.tar
The result must match the web report.
If it does not match, the artifact is not trusted.


## License

MIT
