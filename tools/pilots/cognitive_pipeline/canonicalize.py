#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
import unicodedata

class CanonError(Exception):
    pass

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_utf8_strict(path: str) -> str:
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CanonError("UTF-8 BOM not allowed")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        raise CanonError(f"Invalid UTF-8: {e}")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

def no_duplicate_object_pairs(pairs):
    obj = {}
    seen = set()
    for k, v in pairs:
        if k in seen:
            raise CanonError(f"Duplicate key detected: {k}")
        seen.add(k)
        obj[k] = v
    return obj

def normalize_unicode(obj):
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [normalize_unicode(x) for x in obj]
    if isinstance(obj, dict):
        return {unicodedata.normalize("NFC", k): normalize_unicode(v) for k, v in obj.items()}
    return obj

def validate_no_floats(obj, path="$"):
    if isinstance(obj, float):
        raise CanonError(f"Float not allowed at {path}")
    if isinstance(obj, list):
        for i, x in enumerate(obj):
            validate_no_floats(x, f"{path}[{i}]")
    if isinstance(obj, dict):
        for k, v in obj.items():
            validate_no_floats(v, f"{path}.{k}")

def canonicalize(path: str) -> bytes:
    text = read_utf8_strict(path)
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=no_duplicate_object_pairs
        )
    except Exception as e:
        raise CanonError(f"Invalid JSON: {e}")

    parsed = normalize_unicode(parsed)
    validate_no_floats(parsed)

    canonical_str = json.dumps(
        parsed,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    canonical_str = canonical_str.replace("\r\n", "\n").replace("\r", "\n")

    if not canonical_str.endswith("\n"):
        canonical_str += "\n"

    return canonical_str.encode("utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output")
    parser.add_argument("--print-sha256", action="store_true")
    args = parser.parse_args()

    try:
        canonical_bytes = canonicalize(args.input)
    except CanonError as e:
        sys.stderr.write(f"CANON_FAIL: {e}\n")
        sys.exit(2)

    if args.output:
        with open(args.output, "wb") as f:
            f.write(canonical_bytes)

    if args.print_sha256:
        print(sha256_hex(canonical_bytes))

if __name__ == "__main__":
    main()
