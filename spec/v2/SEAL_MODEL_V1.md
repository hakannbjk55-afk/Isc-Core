
## Registry Snapshot Identity

Registry snapshot id is computed as:
  SHA256( "ISC_REGISTRY_V1\0" || SHA256(canonicalize(registry_json)) )

Raw file SHA256 MAY be included as informational only.
It is NOT normative.

Rationale: Core canonicalization is the single canonical authority.
Raw byte dependency would make snapshot id format-sensitive.
