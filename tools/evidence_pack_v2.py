#!/usr/bin/env python3
import os, tarfile, hashlib

OUT_TAR = "artifacts/evidence_pack_v2.tar"
OUT_MANIFEST = "artifacts/evidence_pack_manifest_v2.sha256"

INCLUDE = [
  "artifacts/ci_report.json",
  "artifacts/evidence_pack_manifest_v1.sha256",
  "artifacts/time_layer_v1_signed/attestation.json",
  "artifacts/time_layer_v1_signed/attestation_hash.txt",
  "artifacts/time_layer_v1_signed/attestation_hash.txt.sig",
  "artifacts/time_layer_v1_signed/attestation_proof.json",
  "artifacts/time_layer_v1_signed/keys/allowed_signers",
    "artifacts/artifact_manifest_v1.json",
    "artifacts/artifact_manifest_v1.sha256",
  "artifacts/time_layer_v1_signed/keys/time_layer_signing_ed25519.pub",
    "artifacts/governance/rotation_commit.json",
    "artifacts/governance/rotation_commit_hash.txt",
    "artifacts/governance/rotation_commit_hash.txt.sig",
    "artifacts/governance/governance_allowed_signers",
    "artifacts/governance/revocation_record.json",
    "artifacts/governance/revocation_record_hash.txt",
    "artifacts/governance/revocation_record_hash.txt.sig",
    "artifacts/governance/revocation_record_hash.txt",
    "artifacts/governance/revocation_record_hash.txt.sig",
]

def sha256_file(path):
  h = hashlib.sha256()
  with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      h.update(chunk)
  return h.hexdigest()

def add_file(tf, path):
  st = os.stat(path)
  ti = tarfile.TarInfo(name=path)
  ti.size = st.st_size
  ti.mode = 0o644
  ti.uid = 0
  ti.gid = 0
  ti.uname = ""
  ti.gname = ""
  ti.mtime = 0
  with open(path, "rb") as f:
    tf.addfile(ti, fileobj=f)

def main():
  missing = [p for p in INCLUDE if not os.path.isfile(p)]
  if missing:
    raise SystemExit("missing inputs:\n" + "\n".join(missing))

  os.makedirs("artifacts", exist_ok=True)

  for p in sorted(INCLUDE):
    pass

  with tarfile.open(OUT_TAR, "w") as tf:
    for p in sorted(INCLUDE):
      add_file(tf, p)

  digest = sha256_file(OUT_TAR)
  with open(OUT_MANIFEST, "w") as f:
    f.write(f"{digest}  {OUT_TAR}\n")

  print("[EVIDENCE_PACK_V2] Wrote:", OUT_TAR)
  print("[EVIDENCE_PACK_V2] SHA256:", digest)
  print("[EVIDENCE_PACK_V2] Manifest:", OUT_MANIFEST)

if __name__ == "__main__":
  main()
