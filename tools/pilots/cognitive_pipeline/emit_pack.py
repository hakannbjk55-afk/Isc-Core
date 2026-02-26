#!/usr/bin/env python3
import argparse, hashlib, json, tarfile, io, sys
from pathlib import Path

def sha256_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha256_bytes(b): return hashlib.sha256(b).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("--case-dir", required=True)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--case-id", default="CPV1-CASE-001")
args = parser.parse_args()

base = Path(args.case_dir)
out  = Path(args.output_dir)
out.mkdir(parents=True, exist_ok=True)

files = sorted([
    "policy.json","payload.json",
    "policy.canon.json","payload.canon.json",
    "ci_report.json","verdict.json"
])

digests = {f: sha256_file(base/f) for f in files}

manifest = {
    "spec_id":"ISC_COGNITIVE_PIPELINE_V1",
    "spec_version":"1.0.0",
    "case_id":args.case_id,
    "files": [{"name":f,"sha256":digests[f]} for f in files]
}
manifest_bytes = (json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode("utf-8")

digests_lines = "".join(f"SHA256 ({f}) = {digests[f]}\n" for f in files)
digests_lines += f"SHA256 (MANIFEST.json) = {sha256_bytes(manifest_bytes)}\n"
digests_bytes = digests_lines.encode("utf-8")

# deterministic tar: lexicographic order, fixed mtime=0
tar_path = out / "EVIDENCE_PACK.tar"
with tarfile.open(tar_path, "w") as tf:
    def add(name, data):
        info = tarfile.TarInfo(name=name)
        info.size  = len(data)
        info.mtime = 0
        info.mode  = 0o644
        info.uid   = 0; info.gid = 0
        info.uname = ""; info.gname = ""
        tf.addfile(info, io.BytesIO(data))
    for f in files:
        add(f, (base/f).read_bytes())
    add("MANIFEST.json", manifest_bytes)
    add("DIGESTS.txt",   digests_bytes)

pack_hash = sha256_file(tar_path)
final_digests = digests_lines + f"SHA256 (EVIDENCE_PACK.tar) = {pack_hash}\n"
final_digests += f"GOLDEN_HASH = {pack_hash}\n"
(out/"DIGESTS.txt").write_text(final_digests, encoding="utf-8")
(out/"MANIFEST.json").write_bytes(manifest_bytes)

print(f"EVIDENCE_PACK.tar written: {tar_path}")
print(f"GOLDEN_HASH: {pack_hash}")
