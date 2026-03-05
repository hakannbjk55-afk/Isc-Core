# ISC Core

ISC Core is a portable, cryptographically verifiable proof format for digital events.

It produces **evidence packs** — small, tamper-evident bundles that allow anyone to independently verify that a release, deployment, or pipeline event actually occurred, who authorized it, and which artifacts were produced.

Evidence packs are designed to be portable (a single file that can be shared or archived), independently verifiable (no platform dependency), and audit-ready (governance, signatures, and lineage included).

> Logs are claims. Evidence packs are proof.

## What is an evidence pack?

An evidence pack proves:

> This event occurred, under this governance, producing these artifacts, derived from these inputs, and existed at this time.

Each pack contains:

- **Content integrity** — all files cryptographically hashed
- **Governance proof** — allowed signers, revocation records, key rotation
- **Time attestation** — signed timestamp proof
- **Artifact lineage** — pipeline derivation chain (V2)

## Verify a release

Download the verifier binary from [Releases](https://github.com/hakannbjk55-afk/Isc-Core/releases):

```bash
curl -L https://github.com/hakannbjk55-afk/Isc-Core/releases/download/v0.2.0/isc_verify -o isc_verify
chmod +x isc_verify
./isc_verify evidence_pack.tar
Expected output:
Content integrity:  valid
Pack identity:      valid
Governance:         1 key(s), 0 revoked
Signatures:         3 verified
Governance:         valid
Lineage:            skipped (V1 pack, no parents)
Anchor:             skipped (use --verify-anchor to check on-chain)

PACK VERIFIED
Verifier options
isc_verify evidence_pack.tar
isc_verify evidence_pack.tar --verify-anchor
isc_verify evidence_pack.tar --verify-anchor --rpc-url <url>
isc_verify --version
Specification
Evidence Pack V2 — Core Specification
Verifier Specification V2
BuildSeal
BuildSeal seals your CI releases and generates a shareable verification link.
→ buildseal.io
License
MIT
