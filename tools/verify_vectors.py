#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "vectors" / "manifest.json"
CASES_DIR = ROOT / "vectors" / "cases"

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)

def main() -> int:
    if not MANIFEST.exists():
        fail("vectors/manifest.json missing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("manifest.cases must be a non-empty list")

    for c in cases:
        case_dir = CASES_DIR / c
        inp = case_dir / "input.json"
        if not inp.exists():
            fail(f"case missing input.json: {c}")

        obj = json.loads(inp.read_text(encoding="utf-8"))
        if obj.get("format") != "isc_report_v1":
            fail(f"{c}: wrong format (expected isc_report_v1)")

        if "errors" not in obj or not isinstance(obj["errors"], list):
            fail(f"{c}: errors must be list")

    print("OK: vectors verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())