# # ISC Core

ISC Core is a deterministic verification core for ISC report bundles.

This repository contains:
- `isc_verify/` : verifier binary (Rust)
- `vectors/` : golden test vectors (valid/invalid cases)
- `tools/` : vector verification utilities

## Requirements
Python 3.10+ and Rust (cargo).

## Quick Start
git clone https://github.com/hakannbjk55-afk/Isc-Core.git && cd Isc-Core && python3 tools/verify_vectors.py

## Build Verifier
cd isc_verify && cargo build --release && ./target/release/isc_verify --version

## Notes
Golden vectors are the canonical regression baseline. Any format/schema change MUST preserve determinism and ship updated vectors.