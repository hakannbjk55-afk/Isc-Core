#!/usr/bin/env python3
import hashlib
import json
import os
import sys
from typing import Any, Dict, List

MANIFEST_PATH = os.path.join("test_vectors", "manifest.json")

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def die(msg: str, code: int = 1) -> None:
    print(f"[VECTOR] ERROR: {msg}")
    sys.exit(code)

def load_manifest() -> Dict[str, Any]:
    if not os.path.isfile(MANIFEST_PATH):
        die(f"Missing manifest: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        try:
            m = json.load(f)
        except Exception as e:
            die(f"Invalid JSON in manifest: {e}")
    if not isinstance(m, dict):
        die("Manifest root must be an object")
    if m.get("version") != 1:
        die("Manifest 'version' must be 1")
    vecs = m.get("vectors")
    if not isinstance(vecs, list) or len(vecs) == 0:
        die("Manifest 'vectors' must be a non-empty array")
    return m

def normalize_path(p: str) -> str:
    p2 = os.path.normpath(p).replace("\\", "/")
    if p2.startswith("../") or p2.startswith("..\\") or p2 == "..":
        die(f"Disallowed path traversal: {p}")
    return p2

def main() -> int:
    update = ("--update" in sys.argv)
    m = load_manifest()
    vecs: List[Dict[str, Any]] = m["vectors"]

    seen = set()
    had_error = False

    # basic sanity: stable ordering recommended
    paths = []
    for i, v in enumerate(vecs):
        if not isinstance(v, dict):
            die(f"vectors[{i}] must be an object")
        path = v.get("path")
        exp = v.get("sha256")
        if not isinstance(path, str) or not path:
            die(f"vectors[{i}].path must be a non-empty string")
        if not isinstance(exp, str) or not exp:
            die(f"vectors[{i}].sha256 must be a non-empty string")
        path = normalize_path(path)
        if path in seen:
            die(f"Duplicate vector path: {path}")
        seen.add(path)
        paths.append(path)

    # warn if not sorted (doesn't fail; you can make it fail later)
    if paths != sorted(paths):
        print("[VECTOR] WARNING: manifest vectors are not sorted by path")

    for v in vecs:
        path = normalize_path(v["path"])
        if not os.path.isfile(path):
            print(f"[VECTOR] FAIL: missing file: {path}")
            had_error = True
            continue

        got = sha256_file(path)
        exp = v["sha256"]

        if update:
            v["sha256"] = got
            print(f"[VECTOR] UPDATE: {path} sha256={got}")
            continue

        if got != exp:
            print(f"[VECTOR] FAIL: {path}")
            print(f"         expected: {exp}")
            print(f"         got:      {got}")
            had_error = True
        else:
            print(f"[VECTOR] OK:   {path}")

    if update:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[VECTOR] Manifest updated: {MANIFEST_PATH}")
        return 0

    return 1 if had_error else 0

if __name__ == "__main__":
    raise SystemExit(main())
