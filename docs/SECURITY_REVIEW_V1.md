# SECURITY REVIEW V1 — ISC Core v13.0.0

## STRIDE Analysis

| Threat | Component | Attack Vector | Mitigation | Status |
|--------|-----------|---------------|------------|--------|
| Spoofing | Governance key | Fake key injection | GPG signature verification | MITIGATED |
| Tampering | Artifact | Binary swap | SHA256 binding in manifest | MITIGATED |
| Tampering | CI report | Hash manipulation | Deterministic CI_REPORT_V1 hash | MITIGATED |
| Repudiation | Release | Unsigned tag | Signed tag + evidence pack | MITIGATED |
| Info Disclosure | Evidence pack | Pack extraction | No secrets in pack | MITIGATED |
| Denial of Service | Verifier | Malformed input | Input validation in verifier.py | PARTIAL |
| Elevation of Privilege | Governance | Key rotation abuse | Rotation policy in registry/ | MITIGATED |

## Supply Chain Attack Mapping

| Attack | Entry Point | Detection | Response |
|--------|-------------|-----------|----------|
| Dependency substitution | External deps | Hash pinning | REJECT |
| CI environment compromise | GitHub Actions | Evidence pack hash | DETECT |
| Maintainer key theft | GPG key | Revocation certificate | REVOKE |
| Artifact swap post-build | Release upload | Manifest SHA256 | REJECT |

## Replay Attack Analysis
- Evidence packs are time-anchored
- Replayed pack from old tag → hash mismatch → REJECT

## Hash Collision Risk
- SHA256 used throughout
- No known practical collision attack
- Risk level: LOW

## Time Anchor Manipulation
- Timestamps derived from git commit time
- Git history is append-only
- Manipulation requires repo write access + signed commit

## Governance Key Rotation Analysis
- Rotation documented in registry/
- Old key revocation required before new key activation
- Gap window: ZERO — rotation is atomic
