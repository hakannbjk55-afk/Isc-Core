#!/usr/bin/env python3

import json
import re
from typing import Any


_SCI_PATTERN = re.compile(r'-?\d+(\.\d+)?[eE][+-]?\d+')


def canonicalize(obj: Any) -> str:
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
    if len(sys.argv) != 2:
        print("usage: canonicalize.py '<json>'", file=sys.stderr)
        raise SystemExit(2)
    raw = sys.argv[1]
    if _SCI_PATTERN.search(raw):
        raise SystemExit(3)
    obj = json.loads(raw)
    print(canonicalize(obj), end="")
