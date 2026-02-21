#!/usr/bin/env python3

import json
import re

MAX_DEPTH = 64

class CanonicalError(ValueError):
    def __init__(self, code: str, msg: str = ""):
        super().__init__(f"{code}:{msg}" if msg else code)
        self.code = code

def _depth_check(obj, depth=0):
    if depth > MAX_DEPTH:
        raise CanonicalError("DEPTH_LIMIT_EXCEEDED", f"depth>{MAX_DEPTH}")
    if isinstance(obj, dict):
        for v in obj.values():
            _depth_check(v, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            _depth_check(v, depth + 1)
from typing import Any


_SCI_PATTERN = re.compile(r'-?\d+(\.\d+)?[eE][+-]?\d+')


def canonicalize(obj: Any) -> str:
    _depth_check(obj, 0)
    # Minimal canonical JSON: sorted keys, no spaces, UTF-8, newline at end
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def parse_input(value: Any) -> Any:
    # Vectors may store input_json as an object OR as a JSON string.
    # v1 policy: scientific notation MUST be rejected.
    if isinstance(value, str):
        if _SCI_PATTERN.search(value):
            raise ValueError("SCIENTIFIC_NOTATION")
        return json.loads(value)
    return value


def canonicalize_from_vector(vector: dict) -> str:
    src = vector.get("input_json")
    if src is None:
        raise ValueError("vector missing input_json")
    return canonicalize(parse_input(src))

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("usage: canonicalize.py '<json>'", file=sys.stderr)
        raise SystemExit(2)

    raw = sys.argv[1]

    try:
        obj = json.loads(raw)
        sys.stdout.write(canonicalize(obj))
        raise SystemExit(0)

    except CanonicalError as e:
        # Stable error line for parity with Rust: CODE:message
        msg = e.args[0] if e.args else ""
        print(f"{e.code}:{msg}", file=sys.stderr)
        raise SystemExit(10)

    except Exception as e:
        print(f"INVALID_JSON:{e}", file=sys.stderr)
        raise SystemExit(11)

