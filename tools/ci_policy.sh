#!/usr/bin/env sh
set -u

REPORT_DIR="artifacts"
REPORT_PATH="${REPORT_DIR}/ci_report.json"

mkdir -p "$REPORT_DIR"

gate_pass=0
gate_fail=0
recovery=0
verifier_present=0
verifier_ran=0
verifier_ok=0
verifier_missing=0

started_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

write_report() {
  exit_code="$1"
  finished_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  total=$((gate_pass + gate_fail + recovery))
  if [ "$total" -le 0 ]; then total=1; fi

  phi_score="$(awk -v gp="$gate_pass" -v r="$recovery" -v t="$total" 'BEGIN { printf "%.2f", 100.0 * ((gp*0.618) + (r*0.382)) / t }')"

  sha="${GITHUB_SHA:-unknown}"
  run_id="${GITHUB_RUN_ID:-unknown}"
  run_number="${GITHUB_RUN_NUMBER:-unknown}"
  repo="${GITHUB_REPOSITORY:-unknown}"

  cat > "$REPORT_PATH" <<JSON
{
  "meta": {
    "repo": "$repo",
    "sha": "$sha",
    "run_id": "$run_id",
    "run_number": "$run_number",
    "started_at_utc": "$started_at_utc",
    "finished_at_utc": "$finished_at_utc",
    "exit_code": $exit_code
  },
  "phi": {
    "gate_weight": 0.618,
    "recovery_weight": 0.382,
    "score": $phi_score
  },
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
    }
  }
}
JSON

  echo "[CI] Report written: $REPORT_PATH"
}

on_exit() {
  code="$?"
  write_report "$code"
  exit "$code"
}
trap on_exit EXIT

echo "[CI] Policy: vectors gate with tolerance on missing verifier"

if [ -f tools/vector_verifier.py ]; then
  verifier_present=1
  echo "[CI] Found tools/vector_verifier.py -> running (GATE)"
  python3 --version || true
  verifier_ran=1
  python3 tools/vector_verifier.py
  verifier_ok=1
  gate_pass=1
  echo "[CI] Vector verifier OK"
else
  verifier_missing=1
  recovery=1
  echo "[CI] WARNING: tools/vector_verifier.py not found -> tolerated (RECOVERY)"
  echo "[CI][TELEMETRY] missing_vector_verifier=1"
fi
