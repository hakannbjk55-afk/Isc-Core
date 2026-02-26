#!/usr/bin/env python3
import argparse, hashlib, sys
from pathlib import Path

def sha256_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("--golden-dir", required=True)
args = parser.parse_args()

golden_dir = Path(args.golden_dir)
pack = golden_dir / "EVIDENCE_PACK.tar"
digests_txt = (golden_dir / "DIGESTS.txt").read_text(encoding="utf-8")

golden_hash = None
for line in digests_txt.splitlines():
    if line.startswith("GOLDEN_HASH"):
        golden_hash = line.split("=")[1].strip()
        break

if not golden_hash:
    print("FAIL: GOLDEN_HASH not found in DIGESTS.txt")
    sys.exit(1)

actual = sha256_file(pack)
if actual == golden_hash:
    print(f"OK: GOLDEN_HASH match: {actual}")
    sys.exit(0)
else:
    print(f"FAIL: hash mismatch")
    print(f"  expected: {golden_hash}")
    print(f"  actual:   {actual}")
    sys.exit(1)
