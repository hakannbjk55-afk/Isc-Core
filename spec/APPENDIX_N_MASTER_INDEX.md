# Appendix N — Master Index & Normative Dependency Graph (Seed)

## N.0 Status
This appendix is NORMATIVE.

## N.1 Purpose
This document is the single source of truth for:
- normative document index
- normative dependency graph (DAG)
- registries (structs, error codes, exit codes)
- precedence rules (MUST/SHOULD override)

## N.2 Normative Documents (Index)
- spec/VERDICT_SPEC.md
- spec/CANONICALIZATION.md
- spec/ERROR_CODES.md
- spec/EVIDENCE_BLOB.md
- spec/MEMBRANE_PROTOCOLS.md

## N.3 Registries (Single Source of Truth)
### N.3.1 Error Code Registry
- spec/ERROR_CODES.md

### N.3.2 Exit Code Registry
- (TBD) spec/EXIT_CODES.md

### N.3.3 Struct Registry
- (TBD) spec/STRUCT_REGISTRY.md

## N.4 MUST/SHOULD Precedence
- NORMATIVE text overrides NON-NORMATIVE text.
- MUST rules override SHOULD rules if both apply.
- If a field is OPTIONAL, absence MUST be treated distinctly from a present null.

## N.5 Normative Dependency Graph (DAG)
- spec/VERDICT_SPEC.md -> spec/CANONICALIZATION.md
- spec/VERDICT_SPEC.md -> spec/ERROR_CODES.md
- spec/EVIDENCE_BLOB.md -> spec/CANONICALIZATION.md
- spec/MEMBRANE_PROTOCOLS.md -> spec/ERROR_CODES.md

## N.6 Change Control
Any change to N.2 or N.5 MUST be reviewed as a governance change.