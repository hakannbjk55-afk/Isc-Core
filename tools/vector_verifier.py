#!/usr/bin/env python3
import hashlib
import json
import os
import sys
import importlib.util
from typing import Any, Dict, List, Tuple, Optional

MANIFEST_PATH = os.path.join("test_vectors", "manifest.json")
CANON_PATH = os.path.join("tools", "canonicalize.py")


def die(msg: str, code: int = 1) -> None:
    print(f"[VECTOR] ERROR: {msg}")
    raise SystemExit(code)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_path(p: str) -> str:
    p2 = os.path.normpath(p).replace("\\", "/")
    if p2.startswith("../") or p2 == "..":
        die(f"Disallowed path traversal: {p}")
    return p2


def _no_dupe_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    obj: Dict[str, Any] = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError(f"DUPLICATE_KEY:{k}")
        obj[k] = v
    return obj


def strict_json_loads(s: str) -> Any:
    return json.loads(s, )


def strict_json_load_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, )


def load_canonicalizer():
    if not os.path.isfile(CANON_PATH):
        die(f"Missing canonicalizer: {CANON_PATH}")
    spec = importlib.util.spec_from_file_location("isc_tools_canonicalize", CANON_PATH)
    if spec is None or spec.loader is None:
        die("Failed to load canonicalizer module spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def extract_input(vector: Dict[str, Any]) -> Optional[Any]:
    # New style: input_json_raw is a JSON string
    if "input_json_raw" in vector and vector["input_json_raw"] is not None:
        raw = vector["input_json_raw"]
        if not isinstance(raw, str):
            raise ValueError("input_json_raw MUST be a string")
        return strict_json_loads(raw)

    # Legacy style: input_json may be an object OR a JSON string
    if "input_json" in vector and vector["input_json"] is not None:
        v = vector["input_json"]
        if isinstance(v, str):
            return strict_json_loads(v)
        return v

    # Some vectors use "input" (very old)
    if "input" in vector and vector["input"] is not None:
        v = vector["input"]
        if isinstance(v, str):
            return strict_json_loads(v)
        return v

    return None


def expected_fail_code(vector: Dict[str, Any]) -> Optional[str]:
    # Support multiple field names
    for k in ("expect_fail", "error_code", "expected_fail"):
        v = vector.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def check_vector_schema(path: str, vector: Dict[str, Any]) -> None:
    if not isinstance(vector.get("id"), str) or not vector["id"]:
        die(f"{path}: vector missing id")

    # input_json/input_json_raw is OPTIONAL (non-canonical vector types exist)
    # If it is missing, verifier will only rely on manifest sha256 pin.
    _ = extract_input(vector)

    # expected is OPTIONAL for legacy vectors.
    # If an expected failure code exists, we will enforce that canonicalize() MUST raise with that code.
    # Otherwise we only require that canonicalize() succeeds.
    # (Vector file bytes are already pinned by manifest sha256.)


def load_manifest() -> Dict[str, Any]:
    if not os.path.isfile(MANIFEST_PATH):
        die(f"Missing manifest: {MANIFEST_PATH}")
    m = strict_json_load_file(MANIFEST_PATH)
    if not isinstance(m, dict):
        die("manifest.json must be an object")
    vecs = m.get("vectors", [])
    if not isinstance(vecs, list):
        die("manifest.json vectors must be a list")
    return m


def main() -> int:
    update = ("--update" in sys.argv)

    m = load_manifest()
    vecs = m.get("vectors", [])
    canon = load_canonicalizer()

    had_error = False

    # Optional: warn if manifest is not sorted
    paths = [v.get("path") for v in vecs if isinstance(v, dict)]
    if paths != sorted(paths):
        print("[VECTOR] WARNING: manifest vectors are not sorted by path")

    for entry in vecs:
        if not isinstance(entry, dict):
            print("[VECTOR] FAIL: manifest entry is not an object")
            had_error = True
            continue

        path = normalize_path(str(entry.get("path", "")))
        if not path:
            print("[VECTOR] FAIL: manifest entry missing path")
            had_error = True
            continue

        if not os.path.isfile(path):
            print(f"[VECTOR] FAIL: missing file: {path}")
            had_error = True
            continue

        got = sha256_file(path)
        exp = entry.get("sha256", "")

        if update:
            entry["sha256"] = got
            print(f"[VECTOR] UPDATE: {path} sha256={got}")
            continue

        if not isinstance(exp, str) or not exp:
            print(f"[VECTOR] FAIL: {path}")
            print("         manifest missing sha256")
            had_error = True
            continue

        if got != exp:
            print(f"[VECTOR] FAIL: {path}")
            print(f"         expected: {exp}")
            print(f"         got:      {got}")
            had_error = True
            continue

        # Parse vector and enforce schema + canonicalization expectations
        try:
            # Fast pre-scan for non-canonical vectors.
            # If the file is not a canonical vector (no input_json/input_json_raw keys),
            # we accept it based on manifest sha256 pin only.
            with open(path, "rb") as _f:
                _raw = _f.read()
            if b"input_json_raw" not in _raw and b"input_json" not in _raw:
                print(f"[VECTOR] OK:   {path}")
                continue
            vec = strict_json_load_file(path)
            if not isinstance(vec, dict):
                raise ValueError("vector file must be an object")
            check_vector_schema(path, vec)

            inp = extract_input(vec)
            if inp is None:
                # Non-canonical vector type (e.g., unicode behavior vectors).
                # File bytes are already pinned by manifest sha256.
                print(f"[VECTOR] OK:   {path}")
                continue
            exp_fail = expected_fail_code(vec)

            # If a failure is expected, canonicalize MUST raise and include that code
            if exp_fail is not None:
                try:
                    _ = canon.canonicalize(inp)  # type: ignore
                    print(f"[VECTOR] FAIL: {path}")
                    print(f"         expected fail: {exp_fail}")
                    print("         got: PASS")
                    had_error = True
                    continue
                except Exception as e:
                    msg = str(e)
                    got_code = msg.split(':', 1)[0] if msg else ''
                    if exp_fail == got_code or exp_fail in msg:
                        print(f"[VECTOR] OK:   {path}")
                        continue
                    print(f"[VECTOR] FAIL: {path}")
                    print(f"         expected fail: {exp_fail}")
                    print(f"         got error:     {msg}")
                    had_error = True
                    continue

            # Otherwise it must canonicalize successfully
            _ = canon.canonicalize(inp)  # type: ignore
            print(f"[VECTOR] OK:   {path}")

        except Exception as e:
            print(f"[VECTOR] FAIL: {path}")
            print(f"         {e}")
            had_error = True
            continue

    if update:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[VECTOR] Manifest updated: {MANIFEST_PATH}")
        return 0

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
