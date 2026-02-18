#!/usr/bin/env python3
import json
from typing import Any

def canonicalize(obj: Any) -> str:
    # Minimal canonical JSON: sorted keys, no spaces, UTF-8, newline at end
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"

def parse_input(value: Any) -> Any:
    # Vectors may store input_json as an object OR as a JSON string
    if isinstance(value, str):
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
    obj = json.loads(sys.argv[1])
    print(canonicalize(obj), end="")
