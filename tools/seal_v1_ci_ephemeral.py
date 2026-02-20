import base64
import json
import os
import re
import sys
import hashlib
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
except Exception as e:
    print("FAIL:CRYPTOGRAPHY_MISSING", file=sys.stderr)
    raise

RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def key_id_from_pubkey(pubkey_bytes: bytes) -> str:
    if len(pubkey_bytes) != 32:
        raise ValueError("Ed25519 public key must be 32 bytes")
    return "sha256:" + sha256_hex(pubkey_bytes)

def b64_nows(pub: bytes) -> str:
    return base64.b64encode(pub).decode("ascii")

def write_json(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")

def main() -> int:
    # This script generates an ephemeral Ed25519 keypair per CI run.
    # It writes:
    # - artifacts/key_registry.json
    # - artifacts/key_registry.json.sha256
    # - artifacts/ci_ephemeral_ed25519_private_key.b64 (CI-only; SHOULD NOT be published)
    #
    # Downstream step uses the private key to sign pack_hash.

    created_at = utc_now_rfc3339()

    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()

    pub_bytes = pub.public_bytes()
    # cryptography requires explicit encoding/format in recent versions; fallback:
    # We'll derive bytes via raw public bytes from private key.
    # To avoid version issues, use private_bytes/public_bytes with Raw.

    from cryptography.hazmat.primitives import serialization

    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    kid = key_id_from_pubkey(pub_bytes)

    registry = {
        "schema": "KEY_REGISTRY_V1",
        "schema_version": "1",
        "canonicalization_rule_version": "CANON_V1",
        "active_selection_rule": "LATEST_NOT_REVOKED_BY_NOT_BEFORE",
        "registry_created_at": created_at,
        "registry_comment": "CI-run scoped ephemeral key (non-trust-anchor)",
        "keys": [
            {
                "key_id": kid,
                "key_use": "PACK_SEAL_V1",
                "public_key": b64_nows(pub_bytes),
                "created_at": created_at,
                "not_before": created_at,
                "comment": "ephemeral_ci"
            }
        ]
    }

    reg_path = os.path.join("artifacts", "key_registry.json")
    write_json(reg_path, registry)

    with open(reg_path, "rb") as f:
        reg_bytes = f.read()
    reg_hash = sha256_hex(reg_bytes)

    with open(os.path.join("artifacts", "key_registry.json.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{reg_hash}  artifacts/key_registry.json\n")

    # Private key file for downstream signing step (CI-only).
    with open(os.path.join("artifacts", "ci_ephemeral_ed25519_private_key.b64"), "w", encoding="utf-8", newline="\n") as f:
        f.write(base64.b64encode(priv_bytes).decode("ascii") + "\n")

    print("OK:KEY_REGISTRY_WRITTEN")
    print(f"key_id={kid}")
    print(f"registry_sha256={reg_hash}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
