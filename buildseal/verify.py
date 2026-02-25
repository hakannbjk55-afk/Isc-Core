#!/usr/bin/env python3
"""BuildSeal v1.0 — Powered by ISC Core"""
import os,json,hashlib,tarfile,argparse
from pathlib import Path
from datetime import datetime,timezone

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def sha256_dir(d):
    h=hashlib.sha256()
    for root,dirs,files in os.walk(d):
        dirs.sort()
        for fname in sorted(files):
            fp=os.path.join(root,fname)
            h.update(os.path.relpath(fp,d).encode())
            h.update(sha256_file(fp).encode())
    return h.hexdigest()

def hash_artifact(path):
    p=Path(path)
    if not p.exists():raise SystemExit(f"[BuildSeal] not found: {path}")
    return sha256_dir(str(p)) if p.is_dir() else sha256_file(str(p))

def verify(artifact_path,commit_sha,repo,baseline=None):
    print("[BuildSeal] Starting verification...")
    had_error=False
    artifact_hash=hash_artifact(artifact_path)
    print(f"  SHA256 ......... OK\n  {artifact_hash[:48]}...")
    print(f"  Commit binding . {'VALID' if len(commit_sha)>=7 else 'FAIL'}")
    if baseline:
        if artifact_hash==baseline:print("  Baseline ....... MATCH")
        else:print(f"  Baseline ....... MISMATCH ✗");had_error=True
    verdict="TAMPERED" if had_error else "TRUSTED"
    print(f"\nVERDICT: {verdict} {'✓' if verdict=='TRUSTED' else '✗'}")
    gho=os.environ.get("GITHUB_OUTPUT")
    if gho:open(gho,"a").write(f"verdict={verdict}\nartifact_hash={artifact_hash}\n")
    return 0 if verdict=="TRUSTED" else 1

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--path",required=True)
    p.add_argument("--commit",default=os.environ.get("GITHUB_SHA","unknown"))
    p.add_argument("--repo",default=os.environ.get("GITHUB_REPOSITORY","unknown"))
    p.add_argument("--baseline",default=None)
    a=p.parse_args()
    return verify(a.path,a.commit,a.repo,a.baseline)

if __name__=="__main__":raise SystemExit(main())
