# Evidence Pack v1.0

A BuildSeal evidence pack contains integrity, build context, and chain anchoring
proof for a build artifact in a single portable file. Third-party verification
does not depend on the SaaS service being online.

---

## Top-Level Schema

Required fields:

- version
- type
- issued_at_utc
- artifact
- build
- binding
- signing
- isc
- checkpoint

Example:

{
  "version": "1",
  "type": "buildseal.evidence_pack",
  "issued_at_utc": "2026-02-28T14:32:01Z",

  "artifact": {
    "name": "myapp.bin",
    "type": "binary",
    "size_bytes": 1833120,
    "hashes": [
      {"alg": "sha256", "hex": "a3f9c1..."}
    ],
    "content_id": "sha256:a3f9c1..."
  },

  "build": {
    "builder": {
      "id": "ci:github-actions",
      "repo": "org/repo",
      "run_id": "123",
      "ref": "refs/heads/main",
      "commit": "deadbeef..."
    },
    "environment": {
      "os": "ubuntu-22.04",
      "arch": "x86_64"
    },
    "toolchain": {
      "buildseal": "1.0.0",
      "isc_core": "1.x"
    }
  },

  "binding": {
    "tbs_alg": "sha256",
    "tbs_fields": [
      "version","type","issued_at_utc",
      "artifact","build"
    ],
    "tbs_digest_hex": "9c01ab..."
  },

  "signing": {
    "scheme": "ed25519",
    "public_key": {"kty":"OKP","crv":"Ed25519","x_b64u":"..."},
    "signature_b64u": "...",
    "signed_digest_hex": "9c01ab..."
  },

  "isc": {
    "network": "isc-mainnet",
    "record": {
      "record_type": "evidence_anchor_v1",
      "digest_hex": "9c01ab...",
      "height": 4821,
      "signer": "governance:primary"
    },
    "node_hint": "https://node.buildseal.io"
  },

  "checkpoint": {
    "adapter": "eth-l2-base",
    "chain_id": 8453,
    "tx_id": "0xabc...",
    "block": 18420001,
    "merkle_root_hex": "0xdef...",
    "batch": {
      "size": 1000,
      "index": 42
    }
  }
}

---

## Verification Steps

1. Recompute `tbs_digest_hex` using canonical encoding.
2. Verify the signature over the digest.
3. Validate ISC record digest equality.
4. Verify the Merkle root on-chain via the specified adapter.
5. Recompute the artifact hash and compare.

Output: VALID or INVALID.
---

## Ethereum L2 Anchor Contract (v1)

For eth-l2 adapters, anchoring MUST target a dedicated anchor contract.

checkpoint.contract (string, required for eth-l2 adapters):
- EVM address of the deployed Anchor contract
- Verifier MUST ensure tx.to == checkpoint.contract

Recommended minimal interface:

function anchor(bytes32 merkleRoot, uint64 batchId, bytes32 metaHash) external;

Event:

event Anchored(
    bytes32 merkleRoot,
    uint64 batchId,
    bytes32 metaHash,
    address indexed sender,
    uint256 blockNumber
);

Verification rule:
- The transaction MUST call the anchor() function.
- The emitted Anchored event MUST contain the same merkleRoot as in the evidence pack.
git add spec/EVIDENCE_PACK_V1.md
git commit -m "spec: add Ethereum L2 anchor contract requirements"
pwd
git rev-parse --show-toplevel
