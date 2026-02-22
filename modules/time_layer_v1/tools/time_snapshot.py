#!/usr/bin/env python3
import json, subprocess, hashlib
from datetime import datetime, timezone
import os

def sh(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def sha256_hex(s):
    return hashlib.sha256(s.encode()).hexdigest()

origin = sh(["git","config","--get","remote.origin.url"])
branch = sh(["git","rev-parse","--abbrev-ref","HEAD"])
commit = sh(["git","rev-parse","HEAD"])

repo_binding = f"{origin}#{branch}"
chain_id = sha256_hex("ISC:TIME_LAYER_V1:" + repo_binding)

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

data = {
    "version":"TIME_LAYER_V1",
    "chain_id":chain_id,
    "captured_at_utc":now,
    "source":"local_termux",
    "run_context":{
        "git_origin":origin,
        "git_branch":branch,
        "git_commit":commit
    }
}

os.makedirs("modules/time_layer_v1/out",exist_ok=True)

with open("modules/time_layer_v1/out/time_snapshot.json","w") as f:
    json.dump(data,f,separators=(",",":"))
    f.write("\n")

print("OK: time_snapshot.json created")
