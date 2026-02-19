#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="artifacts"
BUNDLE_DIR="${OUT_DIR}/verifier_bundle_v1"
BUNDLE_TAR="${OUT_DIR}/verifier_bundle_v1.tar"
BUNDLE_SHA="${OUT_DIR}/verifier_bundle_v1.sha256"

rm -rf "$BUNDLE_DIR" "$BUNDLE_TAR" "$BUNDLE_SHA"
mkdir -p "$BUNDLE_DIR"

cp tools/verify_evidence_pack_v1.sh "$BUNDLE_DIR/verify_evidence_pack_v1.sh"
cp spec/core/VERIFIER_BUNDLE_V1.md "$BUNDLE_DIR/VERIFIER_BUNDLE_V1.md"

(
  cd "$BUNDLE_DIR"
  sha256sum VERIFIER_BUNDLE_V1.md verify_evidence_pack_v1.sh > SHA256SUMS
)

tar \
  --sort=name \
  --mtime="UTC 1970-01-01" \
  --owner=0 --group=0 --numeric-owner \
  --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
  -cf "$BUNDLE_TAR" \
  -C "$OUT_DIR" verifier_bundle_v1

sha256sum "$BUNDLE_TAR" > "$BUNDLE_SHA"

echo "[BUNDLE] Wrote: $BUNDLE_TAR"
echo "[BUNDLE] SHA256: $(cat "$BUNDLE_SHA")"
