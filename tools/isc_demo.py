#!/usr/bin/env python3
"""
ISC Core — 30-second demo
No dependencies. Just Python 3.6+

Usage:
    git clone https://github.com/hakannbjk55-afk/Isc-Core
    cd Isc-Core
    python3 tools/isc_demo.py
"""
import hashlib
import json
import os
import sys
import importlib.util
from datetime import datetime, timezone

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║        ISC Core — Cryptographic Moment Proof         ║
║    github.com/hakannbjk55-afk/Isc-Core               ║
╚══════════════════════════════════════════════════════╝
"""

# Repo root = parent of tools/
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))

def load_canon():
    canon_path = os.path.join(REPO_ROOT, "tools", "canonicalize.py")
    spec = importlib.util.spec_from_file_location("canonicalize", canon_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load tools/canonicalize.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_manifest():
    path = os.path.join(REPO_ROOT, "test_vectors", "manifest.json")
    if not os.path.isfile(path):
        print("  ERROR: test_vectors/manifest.json not found")
        print("  Run from repo root:")
        print("    cd Isc-Core && python3 tools/isc_demo.py")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Support both: list manifest OR {"vectors":[...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "vectors" in data and isinstance(data["vectors"], list):
        return data["vectors"]

    raise SystemExit("  ERROR: Unknown manifest format (expected list or {'vectors':[...]}).")

def run_vectors():
    manifest = load_manifest()
    canon = load_canon()

    passed = failed = 0
    total = len(manifest)

    print(f"  Running {total} test vectors...\n")

    for entry in manifest:
        vpath = entry.get("path")
        exp = entry.get("expected_failure")

        if not vpath:
            print("  [FAIL] manifest entry missing 'path'")
            failed += 1
            continue

        full = os.path.join(REPO_ROOT, vpath)

        try:
            with open(full, encoding="utf-8") as f:
                inp = json.load(f)

            if exp:
                try:
                    canon.canonicalize(inp)
                    print(f"  [FAIL] {vpath} (expected failure: {exp})")
                    failed += 1
                except Exception as e:
                    msg = str(e)
                    # Match by prefix or substring to be tolerant
                    if msg.startswith(exp) or exp in msg:
                        print(f"  [OK]   {vpath}")
                        passed += 1
                    else:
                        print(f"  [FAIL] {vpath} expected:{exp} got:{msg}")
                        failed += 1
            else:
                canon.canonicalize(inp)
                print(f"  [OK]   {vpath}")
                passed += 1

        except Exception as e:
            print(f"  [FAIL] {vpath} {e}")
            failed += 1

    return passed, failed, total

def main():
    # Banner (non-fatal if terminal can't render)
    try:
        print(BANNER)
    except Exception:
        print("ISC Core — Cryptographic Moment Proof")

    # Basic repo sanity
    if not os.path.isdir(os.path.join(REPO_ROOT, "tools")) or not os.path.isdir(os.path.join(REPO_ROOT, "test_vectors")):
        print("ERROR: Repo structure not found. Run:")
        print("  cd Isc-Core && python3 tools/isc_demo.py")
        return 1

    print("─" * 54)
    print(" STEP 1: Cryptographic Moment Proof")
    print("─" * 54)

    now = datetime.now(timezone.utc).isoformat()
    payload_obj = {"event": "ISC Core demo", "ts": now}
    payload = json.dumps(payload_obj, sort_keys=True, separators=(",", ":"))  # deterministic JSON text
    proof = sha256_text(payload)
    chain = sha256_text(proof + "|" + now)

    print(f"  Timestamp : {now}")
    print(f"  Payload   : {payload}")
    print(f"  SHA256    : {proof[:32]}...")
    print(f"  Chain     : {chain[:32]}...\n")

    print("  ✓ Deterministic   — same input = same output")
    print("  ✓ Tamper-evident  — any change breaks the hash")
    print("  ✓ Time-bound      — timestamp is part of the proof")
    print("  ✓ Offline         — no server needed to verify\n")

    print("─" * 54)
    print(" STEP 2: Vector Verification")
    print("─" * 54)

    passed, failed, total = run_vectors()

    print("\n" + "─" * 54)
    if failed == 0:
        print(f" VERDICT: PASS ✓  ({passed}/{total} vectors)")
        print("\n ISC Core integrity chain: VALID")
        print(" All moments cryptographically provable.")
        rc = 0
    else:
        print(f" VERDICT: FAIL ✗  ({failed}/{total} vectors failed)")
        print("\n ISC Core integrity chain: BROKEN")
        rc = 1
    print("─" * 54 + "\n")
    print(" Learn more: github.com/hakannbjk55-afk/Isc-Core\n")
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
CTRL + D
python3 tools/isc_demo.py
cd ~/Isc-Core && python3 - <<'PY'
p="tools/isc_demo.py"
s=open(p,"r",encoding="utf-8").read()
s=s.replace('if __name__ == " main ":','if __name__ == "__main__":')
s=s.replace('if __name__ == " __main__ ":','if __name__ == "__main__":')
open(p,"w",encoding="utf-8").write(s)
print("fixed")
PY
CD 
cd ~/Isc-Core && tail -5 tools/isc_demo.py
pkg update -y
pkg install -y python
pip install cryptography --break-system-packages
cd ~/storage/downloads
ls
ls ~/storage
~/Isc-Core
cd ~/Isc-Core
pwd
ls
ls ~
cd /
ls
cd $HOME/Isc-Core
~/Isc-Core
cd ~/Isc-Core
cd $HOME/Isc-Core
pwd
ls
/data/data/com.termux/files/home/Isc-Core
ls ~
pkg update -y
pkg install -y git python
python -V
git --version
