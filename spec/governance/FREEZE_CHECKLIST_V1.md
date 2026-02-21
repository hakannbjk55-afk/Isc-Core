# ISC Core v1 Freeze Checklist (DRAFT)

This checklist defines the minimum conditions required to declare ISC Core v1 as FROZEN.

Once v1 is declared FROZEN, its canonicalization rules and canonical bytes MUST NOT change.
Any change that affects canonical bytes MUST require a MAJOR version bump.

## Current status snapshot

### Completed (verified by vectors / evidence flow)
- Duplicate key handling: DONE
- Deep nesting canonicalization: DONE
- Float precision boundaries: DONE
- Large integer boundary (2^53): DONE
- Evidence pack reproducibility: DONE
- Independent device verification: DONE
- Archive-authoritative verification model: DONE
- Version governance gate: DONE

### Missing / Undefined (must be closed before FROZEN)
- Negative zero policy (e.g., -0 vs 0): MISSING
- Scientific notation policy (e.g., 1e3 forms): MISSING
- Surrogate / invalid code point policy (UTF-8 validity): MISSING
- Line ending policy (LF vs CRLF normalization): MISSING
- Maximum depth / maximum size limits: MISSING
- Error code taxonomy and registry: MISSING
- Vector corpus size target (25-40): INCOMPLETE (current: 10)

## Closure rule
Each missing item MUST be closed by:
- adding a normative spec rule (MUST/SHOULD/MAY), and
- adding at least one test vector that locks the behavior.


### Deferred to v2 (explicitly out-of-scope for v1)
- Cryptographic seal signature (pack signing) as a mandatory requirement
- Cryptographic time anchoring (seal-time binding, TSA/public anchor)
