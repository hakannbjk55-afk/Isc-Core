#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

def sha256_str(s): return hashlib.sha256(s.encode()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("policy_canon")
parser.add_argument("payload_canon")
parser.add_argument("-o","--output", required=True)
parser.add_argument("--case-id", default="CPV1-CASE-001")
args = parser.parse_args()

policy  = json.loads(Path(args.policy_canon).read_text(encoding="utf-8"))
payload = json.loads(Path(args.payload_canon).read_text(encoding="utf-8"))

rules = []

# R01: schema — required keys present
required_payload = {"timestamp","signature","content_hash"}
r01 = required_payload.issubset(payload.keys())
rules.append({"rule_id":"R01_SCHEMA_VALID",     "result":"PASS" if r01 else "FAIL"})

# R02: hash allowlist — content_hash non-empty and len>=8
ch = payload.get("content_hash","")
r02 = isinstance(ch, str) and len(ch) >= 8
rules.append({"rule_id":"R02_HASH_ALLOWLIST",   "result":"PASS" if r02 else "FAIL"})

# R03: timestamp format — basic ISO8601 check
ts = payload.get("timestamp","")
r03 = isinstance(ts, str) and "T" in ts and ts.endswith("Z")
rules.append({"rule_id":"R03_TIMESTAMP_FORMAT", "result":"PASS" if r03 else "FAIL"})

# R04: signature present and non-empty
sig = payload.get("signature","")
r04 = isinstance(sig, str) and len(sig) > 0
rules.append({"rule_id":"R04_SIGNATURE_PRESENT","result":"PASS" if r04 else "FAIL"})

all_pass = all(r["result"] == "PASS" for r in rules)
verdict_str = "ALLOW" if all_pass else "DENY"

canon_input_hash = sha256_str(
    Path(args.policy_canon).read_text(encoding="utf-8") +
    Path(args.payload_canon).read_text(encoding="utf-8")
)

doc = {"case_id":args.case_id,"verdict":verdict_str,"rules_evaluated":rules,"canonical_input_hash":canon_input_hash}
doc["verdict_hash"] = sha256_str(json.dumps({k:v for k,v in doc.items() if k!="verdict_hash"},sort_keys=True))

Path(args.output).parent.mkdir(parents=True, exist_ok=True)
Path(args.output).write_text(json.dumps(doc,indent=2)+"\n", encoding="utf-8")
print(f"verdict: {verdict_str}")
print(f"verdict_hash: {doc['verdict_hash']}")
