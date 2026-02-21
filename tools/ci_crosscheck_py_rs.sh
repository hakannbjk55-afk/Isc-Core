#!/usr/bin/env bash
set -euo pipefail

echo "[XCHECK] Building Rust validator"
cargo build --quiet --manifest-path validator_rs/Cargo.toml

echo "[XCHECK] Running PY vs RS crosscheck"
./tools/crosscheck_py_rs.sh

echo "[XCHECK] OK"
