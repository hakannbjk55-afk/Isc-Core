#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ZERO_PREV = "0" * 64

def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")

def repo_id():
    gh = os.environ.get("GITHUB_REPOSITORY")
    if gh:
        return gh.strip()

    url = sh(["git", "config", "--get", "remote.origin.url"])
    url = url.replace("git@github.com:", "github.com/")
    url = url.replace("https://", "").replace("http://", "")
    if url.endswith(".git"):
        url = url[:-4]
    parts = url.split("/")
    if len(parts) >= 3:
        return f"{parts[-2]}/{parts[-1]}"
    return url

def chain_id_for_repo(repo):
    return hashlib.sha256(("ISC:TIME_LAYER_V1:" + repo).encode("utf-8")).hexdigest()

def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: attest_release.py <STATE_HASH> <PACK_HASH>")

    state_hash = sys.argv[1].lower()
    pack_hash = sys.argv[2].lower()

    for name, v in [("state_hash", state_hash), ("pack_hash", pack_hash)]:
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
            raise SystemExit(f"{name} must be 64-hex")

    repo = repo_id()
    chain_id = chain_id_for_repo(repo)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    commit = sh(["git", "rev-parse", "HEAD"])
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])

    body = {
        "version": "TIME_LAYER_V1",
        "mode": "STATELESS",
        "chain_id": chain_id,
        "repo": repo,
        "prev_attestation_hash": ZERO_PREV,
        "state_hash": state_hash,
        "pack_hash": pack_hash,
        "release": {
            "git_commit": commit,
            "git_branch": branch,
        },
        "anchor": {"type": "none", "ref": ""},
        "proof": {"type": "none"},
        "captured_at_utc": now,
    }

    att_hash = sha256_hex_bytes(canonical_json(body))

    out = dict(body)
    out["attestation_hash"] = att_hash

    os.makedirs("modules/time_layer_v1/out", exist_ok=True)
    with open("modules/time_layer_v1/out/attestation.json", "w", encoding="utf-8") as f:
        f.write(canonical_json(out).decode("utf-8"))
        f.write("\n")

    print("OK: attestation.json created")

if __name__ == "__main__":
    main()
