#!/usr/bin/env python3

import json
import hashlib
import sys
import os
from datetime import datetime, timezone

OUTPUT_JSON = "artifacts/artifact_manifest_v1.json"
OUTPUT_SHA = "artifacts/artifact_manifest_v1.sha256"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def validate_hex64(s):
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)

def main():
    if len(sys.argv) < 2:
        print("Usage: artifact_manifest_v1.py <file1> [file2 ...]")
        sys.exit(1)

    subjects = []

    for path in sys.argv[1:]:
        if not os.path.isfile(path):
            print(f"ERROR: file not found: {path}")
            sys.exit(1)

        digest = sha256_file(path)

        if not validate_hex64(digest):
            print(f"ERROR: invalid sha256 for {path}")
            sys.exit(1)

        subjects.append({
            "type": "file",
            "name": os.path.basename(path),
            "digest_alg": "sha256",
            "digest": digest,
            "source": path
        })

    manifest = {
        "version": "ARTIFACT_BINDING_V1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "subjects": subjects
    }

    os.makedirs("artifacts", exist_ok=True)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(manifest, f, separators=(",", ":"), sort_keys=True)

    manifest_hash = sha256_file(OUTPUT_JSON)

    with open(OUTPUT_SHA, "w") as f:
        f.write(manifest_hash + "\n")

    print("OK: artifact_manifest_v1 generated")
    print(f"SHA256: {manifest_hash}")

if __name__ == "__main__":
    main()
