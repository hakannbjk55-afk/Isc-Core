#!/usr/bin/env python3
import json, os, subprocess, hashlib, sys
from datetime import datetime, timezone

GENESIS_PREV_V1 = "377dbce9465616c6a7b66d6742fa7898292b58c19f8f9dced7820ed32c5b7dc1"

def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def is_hex64(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def canonical_json(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n").encode("utf-8")

def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) < 3:
        print("usage: attest_release.py <state_hash_64hex> <pack_hash_64hex> [prev_attestation_hash_64hex]", file=sys.stderr)
        sys.exit(2)

    state_hash = sys.argv[1].lower()
    pack_hash  = sys.argv[2].lower()
    prev_hash  = (sys.argv[3].lower() if len(sys.argv) >= 4 else GENESIS_PREV_V1)

    if not is_hex64(state_hash): raise SystemExit("state_hash must be 64-hex")
    if not is_hex64(pack_hash):  raise SystemExit("pack_hash must be 64-hex")
    if not is_hex64(prev_hash):  raise SystemExit("prev_attestation_hash must be 64-hex")

    origin = sh(["git", "config", "--get", "remote.origin.url"])
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = sh(["git", "rev-parse", "HEAD"])
    tag = os.environ.get("GIT_TAG", "local")

    repo_binding = f"{origin}#{branch}"
    chain_id = hashlib.sha256(("ISC:TIME_LAYER_V1:" + repo_binding).encode("utf-8")).hexdigest()

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # Body WITHOUT attestation_hash
    body = {
        "version": "TIME_LAYER_V1",
        "chain_id": chain_id,
        "prev_attestation_hash": prev_hash,
        "state_hash": state_hash,
        "pack_hash": pack_hash,
        "release": {
            "git_origin": origin,
            "git_branch": branch,
            "git_commit": commit,
            "tag": tag,
        },
        "anchor": {"type": "none", "ref": ""},
        "proof": {"type": "none"},
        "captured_at_utc": now,
    }

    att_hash = sha256_hex_bytes(canonical_json(body))

    out = {
        "version": "TIME_LAYER_V1",
        "chain_id": chain_id,
        "attestation_hash": att_hash,
        "prev_attestation_hash": prev_hash,
        "state_hash": state_hash,
        "pack_hash": pack_hash,
        "release": body["release"],
        "anchor": body["anchor"],
        "proof": body["proof"],
        "captured_at_utc": now,
    }

    os.makedirs("modules/time_layer_v1/out", exist_ok=True)
    with open("modules/time_layer_v1/out/attestation.json", "w", encoding="utf-8") as f:
        f.write(canonical_json(out).decode("utf-8"))

    print("OK: attestation.json created")

if __name__ == "__main__":
    main()
