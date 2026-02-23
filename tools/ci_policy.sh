#!/usr/bin/env bash
bash tools/version_gate.sh

bash tools/phi_tripwire.sh

set -e

REPORT_PATH="artifacts/ci_report.json"
mkdir -p artifacts

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

gate_pass=0
gate_fail=0
recovery=0

verifier_present=0
verifier_ran=0
verifier_ok=0
verifier_missing=0

manifest_present=0
manifest_vectors=0
manifest_sha256=""

calc_phi() {
  total=$((gate_pass + gate_fail + recovery))
  if [ "$total" -eq 0 ]; then
    echo "0.0"
  else
    python3 - <<PY
total=$total
gate=$gate_pass
print(round((gate/total)*100, 2))
PY
  fi
}

sha256_file() {
  python3 - <<PY
import hashlib, sys
p="test_vectors/manifest.json"
h=hashlib.sha256()
with open(p,"rb") as f:
    h.update(f.read())
print(h.hexdigest())
PY
}

count_vectors() {
  python3 - <<PY
import json
m=json.load(open("test_vectors/manifest.json","r",encoding="utf-8"))
print(len(m.get("vectors",[])))
PY
}

write_report() {
  code="$1"
  phi_score=$(calc_phi)

  if [ -f test_vectors/manifest.json ]; then
    manifest_present=1
    manifest_vectors=$(count_vectors)
    manifest_sha256=$(sha256_file test_vectors/manifest.json)
  fi

  cat > "$REPORT_PATH" <<JSON
{
  "exit_code": $code,
  "phi_health_score": $phi_score,
  "counters": {
    "gate_pass": $gate_pass,
    "gate_fail": $gate_fail,
    "recovery": $recovery
  },
  "checks": {
    "vector_verifier": {
      "present": $verifier_present,
      "ran": $verifier_ran,
      "ok": $verifier_ok,
      "missing": $verifier_missing
    },
    "manifest": {
      "present": $manifest_present,
      "vectors_count": $manifest_vectors,
      "sha256": "$manifest_sha256"
    }
  }
}
JSON

  echo "[CI] Report written: $REPORT_PATH"
}

on_exit() {
  code="$?"
  write_report "$code"
  echo "[CI] Checking deterministic CI report hash (CI_REPORT_V1)"
  python3 tools/ci_report_hash_check.py
echo "[CI] Building Evidence Pack v1"
python tools/evidence_pack_v2.py || true
bash tools/build_evidence_pack_v1.sh
  exit "$code"
}
trap on_exit EXIT

echo "[CI] Policy: vectors gate with tolerance on missing verifier"

if [ -f tools/vector_verifier.py ]; then
  verifier_present=1
  echo "[CI] Found tools/vector_verifier.py -> running (GATE)"
  python3 --version || true
  verifier_ran=1

  if python3 tools/vector_verifier.py; then
    verifier_ok=1
    gate_pass=1
    echo "[CI] Vector verifier OK"
  else
    gate_fail=1
    echo "[CI] Vector verifier FAILED"
    exit 1
  fi
else
  verifier_missing=1
  recovery=1
  echo "[CI] WARNING: tools/vector_verifier.py not found -> tolerated (RECOVERY)"
  echo "[CI][TELEMETRY] missing_vector_verifier=1"
fi

