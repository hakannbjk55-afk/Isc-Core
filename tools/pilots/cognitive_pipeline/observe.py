#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

def sha256_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha256_str(s):  return hashlib.sha256(s.encode()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("policy_canon")
parser.add_argument("payload_canon")
parser.add_argument("-o","--output", required=True)
parser.add_argument("--case-id", default="CPV1-CASE-001")
args = parser.parse_args()

pd = sha256_file(args.policy_canon)
yd = sha256_file(args.payload_canon)

steps = [
  {"step":"env_lock",        "status":"OK",      "digest": sha256_str(json.dumps({"platform":sys.platform,"clock_policy":"locked_to_input_timestamp"},sort_keys=True))},
  {"step":"input_canon",     "status":"OK",      "digest": sha256_str(pd+yd), "inputs":{"policy":pd,"payload":yd}},
  {"step":"state_snapshot",  "status":"OK",      "digest": sha256_str(json.dumps({"policy":pd,"payload":yd,"case_id":args.case_id},sort_keys=True))},
  {"step":"policy_decision", "status":"PENDING", "digest": sha256_str("policy_decision:PENDING")},
  {"step":"artifact_emit",   "status":"PENDING", "digest": sha256_str("artifact_emit:PENDING")},
]

pipeline_digest = sha256_str("".join(s["digest"] for s in steps))

report = {"spec_id":"ISC_COGNITIVE_PIPELINE_V1","spec_version":"1.0.0","case_id":args.case_id,"stage":"observe","steps":steps,"pipeline_digest":pipeline_digest}

Path(args.output).parent.mkdir(parents=True, exist_ok=True)
Path(args.output).write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
print(f"pipeline_digest: {pipeline_digest}")
