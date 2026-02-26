# AUDIT SCOPE — ISC Core v13.0.0

## Version Freeze
- Tag: v13.0.0-audit
- Commit: 79a4a615cd20ddb389ec6de2cb8ff0cfbc7578cc
- Date: 2026-02-26

## Included Modules
- isc_verify/
- modules/
- tools/
- spec/
- registry/
- buildseal/
- validator_rs/
- test_vectors/

## Excluded Modules
- demos/
- proof_demo/
- vectors/
- .github/

## Trust Boundary
- All artifact binding occurs inside isc_verify/
- Governance lifecycle managed via registry/
- CI report hash binding enforced at push time

## Assumptions
- GPG key holder is trusted
- Git history is append-only
- CI environment is not compromised

## Out-of-Scope Components
- GitHub Actions infrastructure
- External dependency supply chain
- Network transport layer

## Reproducibility Claim
Any verifier can reproduce results by running:
  git checkout v13.0.0-audit
  python tools/verifier.py examples/sample_evidence_pack_v2.tar

## Verification Procedure
1. Clone repository
2. Checkout v13.0.0-audit tag
3. Verify tag signature: git verify-tag v13.0.0-audit
4. Run verifier: python tools/verifier.py examples/sample_evidence_pack_v2.tar
5. Compare output hash with AUDIT_MANIFEST_V13.json
