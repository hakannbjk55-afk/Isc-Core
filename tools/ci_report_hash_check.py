#!/usr/bin/env python3
import json
import hashlib
import sys
from pathlib import Path

GOLDEN_PATH = Path("spec/golden/CI_REPORT_V1.sha256")
REPORT_PATH = Path("artifacts/ci_report.json")

def die(msg: str, code: int = 2) -> None:
    print(f"[CI][HASH] {msg}")
    sys.exit(code)

def main() -> int:
    if not GOLDEN_PATH.exists():
        die(f"Missing golden file: {GOLDEN_PATH}", 3)
    if not REPORT_PATH.exists():
        die(f"Missing report file: {REPORT_PATH}", 4)

    golden = GOLDEN_PATH.read_text(encoding="utf-8").strip().lower()
    if not golden or any(c not in "0123456789abcdef" for c in golden) or len(golden) != 64:
        die(f"Invalid golden sha256 in {GOLDEN_PATH}", 5)

    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    # timestamp her çalıştırmada değişebilir; hash'e dahil etmiyoruz
    data.pop("timestamp_utc", None)

    canon = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    got = hashlib.sha256(canon).hexdigest()

    if got != golden:
        print("[CI][HASH] MISMATCH")
        print("  expected:", golden)
        print("  got:     ", got)
        return 6

    print("[CI][HASH] OK:", got)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
