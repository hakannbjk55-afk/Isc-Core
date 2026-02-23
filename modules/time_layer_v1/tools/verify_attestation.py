#!/usr/bin/env python3
import hashlib, json, sys

def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")

def is_hex64(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64: return False
    s = s.lower()
    return all(c in "0123456789abcdef" for c in s)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "modules/time_layer_v1/out/attestation.json"
    with open(path, "r", encoding="utf-8") as f:
        a = json.load(f)

    for k in ["version","chain_id","repo","mode","prev_attestation_hash","state_hash","pack_hash","release","anchor","proof","captured_at_utc","attestation_hash"]:
        if k not in a:
            raise SystemExit(f"{path}: missing field {k}")

    for k in ["chain_id","prev_attestation_hash","state_hash","pack_hash","attestation_hash"]:
        if not is_hex64(a[k]):
            raise SystemExit(f"{path}: invalid hex field {k}")

    body = dict(a)
    att = body.pop("attestation_hash")

    computed = sha256_hex_bytes(canonical_json(body))
    if computed != att:
        raise SystemExit(f"{path}: attestation_hash mismatch")

    print("OK: attestation verified")

if __name__ == "__main__":
    main()
