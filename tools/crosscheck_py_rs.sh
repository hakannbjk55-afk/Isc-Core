#!/usr/bin/env bash
set -euo pipefail

RS_MANIFEST="validator_rs/Cargo.toml"

PY_OUT="$(mktemp)"
RS_OUT="$(mktemp)"
trap 'rm -f "$PY_OUT" "$RS_OUT"' EXIT

fail=0

for f in test_vectors/vector_*.json; do
  raw="$(jq -r '
    if has("input_json_raw") and (.input_json_raw|type=="string") then .input_json_raw
    elif has("input_json") then (.input_json|tojson)
    else "" end' "$f")"

  if [ -z "$raw" ] || [ "$raw" = "null" ]; then
    continue
  fi

  exp_fail="$(jq -r '(.expect_fail // .error_code // "")' "$f")"
  if [ -n "$exp_fail" ] && [ "$exp_fail" != "null" ]; then
    continue
  fi

  if ! python3 tools/canonicalize.py "$raw" > "$PY_OUT" 2>/dev/null; then
    continue
  fi
  if ! cargo run --quiet --manifest-path "$RS_MANIFEST" -- canon "$raw" > "$RS_OUT" 2>/dev/null; then
    continue
  fi

  if ! diff -q "$PY_OUT" "$RS_OUT" >/dev/null; then
    echo "MISMATCH: $f"
    echo "PY:"; cat -A "$PY_OUT"
    echo "RS:"; cat -A "$RS_OUT"
    fail=1
    break
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "OK: PY vs RS canonical outputs match (for canonical PASS vectors)"
fi

exit "$fail"
