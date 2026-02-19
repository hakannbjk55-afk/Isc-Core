#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "[CI_CHECK] Running local gate checks..."

bash tools/phi_tripwire.sh
bash tools/version_gate.sh
bash tools/ci_policy.sh

echo "[CI_CHECK] OK: All checks passed"
