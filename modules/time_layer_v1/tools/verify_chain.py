#!/usr/bin/env python3
import json, hashlib, glob, sys

GENESIS_PREV_V1 = "377dbce9465616c6a7b66d6742fa7898292b58c19f8f9dced7820ed32c5b7dc1"
BASE = "modules/time_layer_v1/out/attestations/*.json"

def canonical_json(obj):
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n").encode("utf-8")

def sha256_hex_bytes(b):
    return hashlib.sha256(b).hexdigest()

def is_hex64(s):
    if not isinstance(s, str) or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

files = sorted(glob.glob(BASE))
if not files:
    raise SystemExit("No attestation files found.")

prev_hash = None
chain_id = None

for i, path in enumerate(files):
    with open(path, "r", encoding="utf-8") as f:
        a = json.load(f)

    # basic checks
    for k in ["version","chain_id","attestation_hash","prev_attestation_hash","state_hash","pack_hash"]:
        if k not in a:
            raise SystemExit(f"{path}: missing field {k}")
        if k != "version" and not is_hex64(a[k]):
            raise SystemExit(f"{path}: invalid hex field {k}")

    # chain_id consistency
    if chain_id is None:
        chain_id = a["chain_id"]
    elif a["chain_id"] != chain_id:
        raise SystemExit(f"{path}: chain_id mismatch")

    # recompute hash
    body = {
        "version": a["version"],
        "chain_id": a["chain_id"],
        "prev_attestation_hash": a["prev_attestation_hash"],
        "state_hash": a["state_hash"],
        "pack_hash": a["pack_hash"],
        "release": a["release"],
        "anchor": a["anchor"],
        "proof": a["proof"],
        "captured_at_utc": a["captured_at_utc"],
    }

    computed = sha256_hex_bytes(canonical_json(body))
    if computed != a["attestation_hash"]:
        raise SystemExit(f"{path}: attestation_hash mismatch")

    # chain linkage
    if i == 0:
        if a["prev_attestation_hash"] != GENESIS_PREV_V1:
            raise SystemExit(f"{path}: first attestation must point to GENESIS")
    else:
        if a["prev_attestation_hash"] != prev_hash:
            raise SystemExit(f"{path}: chain broken")

    prev_hash = a["attestation_hash"]

print("OK: full chain verified")
