# ISC Core Versioning Model

ISC Core uses a hybrid versioning model.

Pack format uses MAJOR version only.
Specification may use MAJOR.MINOR.
Verifier declares supported major versions.

Example:

format_version: V2

Spec versions:

v2.0
v2.1
v2.2

Rules:

- Pack changes that break compatibility require new MAJOR
- Spec clarifications use MINOR
- Verifier must fail on unknown MAJOR
- Minor versions must stay backward compatible


## Pack Version

Stored inside pack metadata.

Example:

format_version: V2

Major version changes when:

- structure changes
- required fields change
- hash rules change
- signature rules change
- canonical rules change
- governance binding changes


## Spec Version

Spec may evolve without changing pack version.

Allowed minor changes:

- optional fields
- docs clarification
- new verifier checks
- optional metadata
- governance extensions


## Verifier Rules

Verifier must:

1. Read format_version
2. Check support
3. Fail if unsupported

Example error:

Unsupported pack format version


## Compatibility

Unknown major version must fail.

Old versions may be supported.

Support is optional.


## Philosophy

Pack must stay verifiable for years.

Version rules must stay simple.

Pack carries only MAJOR.
Spec carries MAJOR.MINOR.

This keeps offline verification stable.
