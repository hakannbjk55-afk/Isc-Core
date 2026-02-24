# ARTIFACT_BINDING_V1

## 1. Purpose

This spec defines how build outputs (artifacts) are cryptographically bound into ISC Core Evidence Pack V2,
so that post-build or deploy-stage tampering (artifact swap) becomes detectable.

This is a module-layer contract. It MUST NOT modify core canonicalization.

## 2. Threat Addressed

Without artifact binding, the following risk exists:

- CI may be correct and evidence pack may verify,
  yet the deployed binary/image could be swapped after build.

ARTIFACT_BINDING_V1 closes this gap by binding artifact digests into the evidence bundle.

## 3. Outputs

The build pipeline MUST produce:

- artifacts/artifact_manifest_v1.json
- artifacts/artifact_manifest_v1.sha256

Both files MUST be included in Evidence Pack V2.

## 4. artifact_manifest_v1.json Format (Normative)

The JSON document MUST have the following top-level fields:

- version: "ARTIFACT_BINDING_V1"
- created_utc: RFC3339 UTC timestamp (e.g., "2026-02-24T00:00:00Z") (declared time)
- subjects: array of subject objects

### 4.1 Subject Object (Normative)

Each subject MUST include:

- type: one of
  - "file" (binary, tarball, apk, etc.)
  - "container_image" (OCI image digest)
  - "sbom" (SBOM file digest)
- name: stable identifier (e.g., filename, image ref)
- digest_alg: MUST be "sha256"
- digest: 64-hex lowercase
- source: optional string (e.g., build step id, path, registry)

Notes:
- For container images, name SHOULD use a stable reference.
  If a tag is used, digest MUST still be the content digest (sha256).
- Digests MUST be lowercase hex.

## 5. artifact_manifest_v1.sha256 (Normative)

This file MUST contain exactly:

- sha256 of artifacts/artifact_manifest_v1.json, lowercase hex, followed by newline.

## 6. Verification Rules (Normative)

Verifier MUST:

1) Confirm both files exist inside the Evidence Pack V2.
2) Recompute sha256(artifact_manifest_v1.json) and compare to artifact_manifest_v1.sha256.
3) Validate all subject digests are 64-hex lowercase.
4) FAIL verification if any rule above fails.

Optional (deployment verification):
- Operator MAY compare deployed artifact digest to a subject entry.
- If mismatch, treat as tampering.

## 7. Non-Goals

ARTIFACT_BINDING_V1 does NOT guarantee:

- external timestamp truth
- correctness of build process
- prevention of key compromise
- registry trust / transparency log inclusion

It provides artifact digest binding only.

