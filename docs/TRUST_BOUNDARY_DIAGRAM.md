# TRUST BOUNDARY DIAGRAM — ISC Core v13.0.0

## Trust Zones

| Zone | Description | Trust Level |
|------|-------------|-------------|
| ZONE-1 | Signed governance registry | TRUSTED |
| ZONE-2 | CI pipeline + artifact builder | CONDITIONAL |
| ZONE-3 | Evidence pack consumer | UNTRUSTED |
| ZONE-4 | External dependency supply chain | UNTRUSTED |

## Boundary Definitions

### ZONE-1 → ZONE-2
- Crossing condition: Valid GPG signature on governance key
- Failure mode: Unsigned or revoked key → REJECT

### ZONE-2 → ZONE-3
- Crossing condition: Evidence pack SHA256 matches manifest
- Failure mode: Hash mismatch → REJECT

### ZONE-4 → ZONE-2
- Crossing condition: Dependency hash pinned in manifest
- Failure mode: Unpinned dependency → WARN

## Invariants
- All artifact binding occurs inside ZONE-1
- No ZONE-3 input can modify ZONE-1 state
- CI report hash is deterministic and append-only

## Offline Verification Guarantee
Verification requires no network access.
All proofs are self-contained in evidence_pack_v2.tar.
