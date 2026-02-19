#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

def stable_json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: ci_report_hash_v1.py <ci_report.json>")
        return 2

    p = Path(sys.argv[1])
    data = json.loads(p.read_text(encoding="utf-8"))

    # runtime-only field, excluded from deterministic hash
    data.pop("timestamp_utc", None)

    h = hashlib.sha256(stable_json_bytes(data)).hexdigest()
    print(h)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
