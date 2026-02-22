#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="artifacts"
OUT_TAR="${OUT_DIR}/evidence_pack_v1.tar"
OUT_SHA="${OUT_DIR}/evidence_pack_v1.sha256"
TMP_TAR="${OUT_TAR}.tmp"
TMP_SHA="${OUT_SHA}.tmp"
MANIFEST="${OUT_DIR}/evidence_pack_manifest_v1.sha256"

mkdir -p "${OUT_DIR}"

FILES=(
  "artifacts/ci_report.json"
  "spec/core/VERSION"
  "test_vectors/manifest.json"
  "tools/ci_policy.sh"
  "tools/version_gate.sh"
    "registry/registry_snapshot.json"
  "tools/phi_tripwire.sh"
)

# Append vector_*.json in deterministic order
while IFS= read -r f; do
  FILES+=("$f")
done < <(find test_vectors -maxdepth 1 -type f -name 'vector_*.json' | LC_ALL=C sort)

# Ensure required files exist (before generating manifest)
for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "[EVIDENCE_PACK] Missing required file: $f" >&2
    exit 71
  fi
done

# Build a deterministic manifest of the pack payload (excluding the tarball itself)
# NOTE: manifest is computed over the exact file list above, in that exact order.
{
  for f in "${FILES[@]}"; do
    sha256sum "$f"
  done
} > "${MANIFEST}"

# Add manifest into the pack
FILES+=("${MANIFEST}")

LC_ALL=C tar \
  --sort=name \
  --numeric-owner --owner=0 --group=0 \
  --mtime='UTC 1970-01-01' \
  --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
  -cf "${TMP_TAR}" \
  "${FILES[@]}"

# Compute hash from TMP_TAR bytes but record the final tar name
hash="$(sha256sum "${TMP_TAR}" | awk '{print $1}')"
printf "%s  %s\n" "$hash" "${OUT_TAR}" > "${TMP_SHA}"

mv -f "${TMP_TAR}" "${OUT_TAR}"
mv -f "${TMP_SHA}" "${OUT_SHA}"

echo "[EVIDENCE_PACK] Wrote: ${OUT_TAR}"
echo "[EVIDENCE_PACK] SHA256: $(cat "${OUT_SHA}")"
echo "[EVIDENCE_PACK] Manifest: ${MANIFEST}"
