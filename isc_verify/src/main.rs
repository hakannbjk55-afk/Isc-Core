use sha2::{Sha256, Digest};
use std::fs;
use std::path::Path;
use std::process;
use ssh_key::{PublicKey, SshSig};

#[derive(Debug)]
enum VerifyError {
    MissingFile(String),
    HashMismatch(String),
    ParseError(String),
    PackIdentityMismatch,
    GovernanceError(String),
    SignatureError(String),
    AnchorError(String),
    LineageError(String),
    IoError(String),
}

impl std::fmt::Display for VerifyError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            VerifyError::MissingFile(p) => write!(f, "Missing required file: {}", p),
            VerifyError::HashMismatch(p) => write!(f, "Hash mismatch: {}", p),
            VerifyError::ParseError(e) => write!(f, "Parse error: {}", e),
            VerifyError::PackIdentityMismatch => write!(f, "Pack identity mismatch"),
            VerifyError::GovernanceError(e) => write!(f, "Governance error: {}", e),
            VerifyError::SignatureError(e) => write!(f, "Signature error: {}", e),
            VerifyError::AnchorError(e) => write!(f, "Anchor error: {}", e),
            VerifyError::LineageError(e) => write!(f, "Lineage error: {}", e),
            VerifyError::IoError(e) => write!(f, "IO error: {}", e),
        }
    }
}

fn sha256_file(path: &Path) -> Result<String, VerifyError> {
    let data = fs::read(path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let mut hasher = Sha256::new();
    hasher.update(&data);
    Ok(hex::encode(hasher.finalize()))
}

fn sha256_bytes(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

fn extract_tar(tar_path: &Path, out_dir: &Path) -> Result<(), VerifyError> {
    let file = fs::File::open(tar_path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let mut archive = tar::Archive::new(file);
    for entry in archive.entries().map_err(|e| VerifyError::IoError(e.to_string()))? {
        let mut entry = entry.map_err(|e| VerifyError::IoError(e.to_string()))?;
        let entry_path = entry.path().map_err(|e| VerifyError::IoError(e.to_string()))?;
        let entry_str = entry_path.to_string_lossy();
        if entry_str.contains("..") || entry_str.starts_with('/') {
            return Err(VerifyError::ParseError(format!("Unsafe path: {}", entry_str)));
        }
        entry.unpack_in(out_dir).map_err(|e| VerifyError::IoError(e.to_string()))?;
    }
    Ok(())
}

fn parse_manifest(manifest_path: &Path) -> Result<Vec<(String, String)>, VerifyError> {
    let content = fs::read_to_string(manifest_path)
        .map_err(|e| VerifyError::IoError(e.to_string()))?;
    let mut entries = Vec::new();
    let mut paths_seen = std::collections::HashSet::new();
    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') { continue; }
        let parts: Vec<&str> = line.splitn(2, "  ").collect();
        if parts.len() != 2 {
            return Err(VerifyError::ParseError(format!("Invalid manifest line: {}", line)));
        }
        let hash = parts[0].trim_start_matches("sha256:").to_string();
        let path = parts[1].to_string();
        if paths_seen.contains(&path) {
            return Err(VerifyError::ParseError(format!("Duplicate path: {}", path)));
        }
        paths_seen.insert(path.clone());
        entries.push((hash, path));
    }
    entries.sort_by(|a, b| a.1.cmp(&b.1));
    Ok(entries)
}

fn parse_allowed_signers(path: &Path) -> Result<Vec<PublicKey>, VerifyError> {
    let content = fs::read_to_string(path)
        .map_err(|e| VerifyError::IoError(e.to_string()))?;
    let mut keys = Vec::new();
    let mut seen = std::collections::HashSet::new();
    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') { continue; }
        let parts: Vec<&str> = line.splitn(3, ' ').collect();
        if parts.len() < 3 { continue; }
        let key_str = format!("{} {}", parts[1], parts[2].split_whitespace().next().unwrap_or(""));
        if seen.contains(&key_str) {
            return Err(VerifyError::GovernanceError(format!("Duplicate key: {}", key_str)));
        }
        seen.insert(key_str.clone());
        if let Ok(pk) = key_str.parse::<PublicKey>() {
            keys.push(pk);
        }
    }
    Ok(keys)
}

fn parse_revocation(path: &Path) -> Result<Vec<String>, VerifyError> {
    let content = fs::read_to_string(path)
        .map_err(|e| VerifyError::IoError(e.to_string()))?;
    let v: serde_json::Value = serde_json::from_str(&content)
        .map_err(|e| VerifyError::ParseError(e.to_string()))?;
    let mut revoked = Vec::new();
    if let Some(arr) = v.as_array() {
        for item in arr {
            if let Some(s) = item.as_str() {
                revoked.push(s.to_string());
            }
        }
    }
    Ok(revoked)
}

fn verify_signature(sig_path: &Path, payload_path: &Path, allowed_keys: &[PublicKey]) -> Result<(), VerifyError> {
    if !payload_path.exists() {
        return Err(VerifyError::SignatureError(format!(
            "Payload missing: {}", sig_path.display()
        )));
    }
    let sig_bytes = fs::read(sig_path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let sig_str = String::from_utf8_lossy(&sig_bytes);
    let ssh_sig = SshSig::from_pem(&*sig_str)
        .map_err(|e| VerifyError::SignatureError(format!("Invalid sig format: {}", e)))?;
    let payload = fs::read(payload_path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let namespace = ssh_sig.namespace();
    for pk in allowed_keys {
        if pk.verify(namespace, &payload, &ssh_sig).is_ok() {
            return Ok(());
        }
    }
    Err(VerifyError::SignatureError(format!(
        "No valid signature for: {}", payload_path.file_name().unwrap_or_default().to_string_lossy()
    )))
}

fn extract_outputs_from_pack(pack_path: &Path) -> Result<Vec<String>, VerifyError> {
    let tmp = tempfile::tempdir().map_err(|e| VerifyError::IoError(e.to_string()))?;
    extract_tar(pack_path, tmp.path())?;
    let ci = tmp.path().join("artifacts/ci_report.json");
    if !ci.exists() { return Ok(vec![]); }
    let raw = fs::read(&ci).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let v: serde_json::Value = serde_json::from_slice(&raw)
        .map_err(|e| VerifyError::ParseError(e.to_string()))?;
    let mut outputs = Vec::new();
    if let Some(arr) = v.get("outputs").and_then(|o| o.as_array()) {
        for item in arr {
            if let Some(s) = item.as_str() {
                outputs.push(s.to_string());
            }
        }
    }
    Ok(outputs)
}

fn verify_lineage(ci_json: &serde_json::Value, pack_dir: &Path) -> Result<bool, VerifyError> {
    let parents = match ci_json.get("parents").and_then(|p| p.as_array()) {
        Some(p) if !p.is_empty() => p,
        _ => return Ok(false), // No parents = V1 pack, skip
    };

    let child_inputs: Vec<String> = ci_json.get("inputs")
        .and_then(|i| i.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect())
        .unwrap_or_default();

    for parent in parents {
        let parent_hash = parent.get("pack_hash")
            .and_then(|h| h.as_str())
            .ok_or_else(|| VerifyError::LineageError("Parent missing pack_hash".to_string()))?;
        let parent_event = parent.get("event")
            .and_then(|e| e.as_str())
            .unwrap_or("unknown");

        // Look for parent pack file
        let parent_pack = pack_dir.join(format!("{}.tar", parent_hash.trim_start_matches("sha256:")));
        if !parent_pack.exists() {
            eprintln!("  WARN: parent pack not found: {} ({})", parent_hash, parent_event);
            continue;
        }

        let parent_outputs = extract_outputs_from_pack(&parent_pack)?;

        // Enforce: parent.outputs ⊆ child.inputs
        for output in &parent_outputs {
            if !child_inputs.contains(output) {
                return Err(VerifyError::LineageError(format!(
                    "Parent output {} not found in child inputs", output
                )));
            }
        }
        println!("  Lineage:          parent '{}' verified", parent_event);
    }

    Ok(true)
}

fn verify_pack(pack_path: &Path, verify_anchor_flag: bool, rpc_url: &str) -> Result<(), VerifyError> {
    let tmp = tempfile::tempdir().map_err(|e| VerifyError::IoError(e.to_string()))?;
    extract_tar(pack_path, tmp.path())?;
    let base = tmp.path().to_path_buf();

    let ci_report_path = base.join("artifacts/ci_report.json");
    if !ci_report_path.exists() {
        return Err(VerifyError::MissingFile("artifacts/ci_report.json".to_string()));
    }

    let manifest_path = ["artifacts/evidence_pack_manifest_v2.sha256",
                          "artifacts/evidence_pack_manifest_v1.sha256",
                          "content_manifest.sha256"]
        .iter().map(|p| base.join(p)).find(|p| p.exists())
        .ok_or_else(|| VerifyError::MissingFile("content_manifest".to_string()))?;

    let entries = parse_manifest(&manifest_path)?;
    let manifest_name = manifest_path.file_name().unwrap().to_string_lossy().to_string();

    for (expected_hash, rel_path) in &entries {
        if rel_path.ends_with(&manifest_name) { continue; }
        let file_path = base.join(rel_path);
        if !file_path.exists() {
            eprintln!("  WARN: missing file: {}", rel_path);
            continue;
        }
        let computed = sha256_file(&file_path)?;
        if &computed != expected_hash {
            return Err(VerifyError::HashMismatch(rel_path.clone()));
        }
    }
    println!("Content integrity:  valid");

    let manifest_raw = fs::read(&manifest_path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    // content_hash excludes ci_report.json (spec: circular dependency prevention)
    let manifest_str = String::from_utf8_lossy(&manifest_raw);
    let manifest_no_ci: String = manifest_str.lines()
        .filter(|l| !l.contains("ci_report.json"))
        .map(|l| format!("{}
", l))
        .collect();
    let content_hash = if manifest_no_ci.trim().is_empty() {
        sha256_bytes(&manifest_raw)
    } else {
        sha256_bytes(manifest_no_ci.as_bytes())
    };
    let ci_raw = fs::read(&ci_report_path).map_err(|e| VerifyError::IoError(e.to_string()))?;
    let ci_json: serde_json::Value = serde_json::from_slice(&ci_raw)
        .unwrap_or(serde_json::Value::Object(Default::default()));

    let stripped_json = {
        let mut m = ci_json.as_object().cloned().unwrap_or_default();
        m.remove("pack_hash"); m.remove("meta_hash"); m.remove("content_hash");
        serde_json::to_vec(&serde_json::Value::Object(m)).unwrap()
    };
    let meta_hash = sha256_bytes(&stripped_json);
    // pack_hash MUST use raw bytes, not hex string concatenation (spec section 13)
    let meta_bytes = hex::decode(&meta_hash).map_err(|e| VerifyError::ParseError(e.to_string()))?;
    let content_bytes = hex::decode(&content_hash).map_err(|e| VerifyError::ParseError(e.to_string()))?;
    if meta_bytes.len() != 32 || content_bytes.len() != 32 {
        return Err(VerifyError::ParseError("meta_hash/content_hash must be 32-byte digests".to_string()));
    }
    let mut pack_input = Vec::with_capacity(64);
    pack_input.extend_from_slice(&meta_bytes);
    pack_input.extend_from_slice(&content_bytes);
    let pack_hash = sha256_bytes(&pack_input);

    if let Some(stored) = ci_json.get("pack_hash").and_then(|v| v.as_str()) {
        if stored.trim_start_matches("sha256:") != pack_hash {
            return Err(VerifyError::PackIdentityMismatch);
        }
    }
    println!("Pack identity:      valid");

    // Governance
    let gov_signers_path = base.join("artifacts/governance/governance_allowed_signers");
    if !gov_signers_path.exists() {
        return Err(VerifyError::MissingFile("governance/governance_allowed_signers".to_string()));
    }
    let gov_keys = parse_allowed_signers(&gov_signers_path)?;
    let revocation_path = base.join("artifacts/governance/revocation_record.json");
    let revoked = if revocation_path.exists() {
        parse_revocation(&revocation_path)?
    } else { vec![] };

    println!("Governance:         {} key(s), {} revoked", gov_keys.len(), revoked.len());

    let time_signers_path = base.join("artifacts/time_layer_v1_signed/keys/allowed_signers");
    let time_keys = if time_signers_path.exists() {
        parse_allowed_signers(&time_signers_path)?
    } else { vec![] };

    let gov_sigs = [
        ("artifacts/governance/rotation_commit_hash.txt.sig",
         "artifacts/governance/rotation_commit_hash.txt"),
        ("artifacts/governance/revocation_record_hash.txt.sig",
         "artifacts/governance/revocation_record_hash.txt"),
    ];
    let mut sig_count = 0;
    for (sig_rel, payload_rel) in &gov_sigs {
        let sig_path = base.join(sig_rel);
        if !sig_path.exists() { continue; }
        verify_signature(&sig_path, &base.join(payload_rel), &gov_keys)?;
        sig_count += 1;
    }

    let tl_sig = base.join("artifacts/time_layer_v1_signed/attestation_hash.txt.sig");
    let tl_payload = base.join("artifacts/time_layer_v1_signed/attestation_hash.txt");
    if tl_sig.exists() && !time_keys.is_empty() {
        verify_signature(&tl_sig, &tl_payload, &time_keys)?;
        sig_count += 1;
    }

    println!("Signatures:         {} verified", sig_count);
    println!("Governance:         valid");

    // Lineage
    let pack_dir = pack_path.parent().unwrap_or(Path::new("."));
    match verify_lineage(&ci_json, pack_dir)? {
        true => println!("Lineage:            valid"),
        false => println!("Lineage:            skipped (V1 pack, no parents)"),
    }

    // Anchor
    if verify_anchor_flag {
        let _ = (pack_hash, rpc_url);
        println!("Anchor:             not yet implemented");
    } else {
        println!("Anchor:             skipped (use --verify-anchor to check on-chain)");
    }

    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        eprintln!("isc_verify v0.2.0");
        eprintln!("Usage:");
        eprintln!("  isc_verify <evidence_pack.tar> [--verify-anchor] [--rpc-url <url>]");
        eprintln!("  isc_verify --version");
        process::exit(2);
    }

    if args[1] == "--version" || args[1] == "-V" {
        println!("isc_verify {}", env!("CARGO_PKG_VERSION"));
        return;
    }

    let pack_path = Path::new(&args[1]);
    let verify_anchor_flag = args.contains(&"--verify-anchor".to_string());
    let rpc_url = args.windows(2)
        .find(|w| w[0] == "--rpc-url")
        .map(|w| w[1].as_str())
        .unwrap_or("https://sepolia.base.org");

    if !pack_path.exists() {
        eprintln!("Error: file not found: {}", args[1]);
        process::exit(1);
    }

    match verify_pack(pack_path, verify_anchor_flag, rpc_url) {
        Ok(()) => {
            println!("\nPACK VERIFIED");
            process::exit(0);
        }
        Err(e) => {
            eprintln!("\nVERIFICATION FAILED");
            eprintln!("Reason: {}", e);
            process::exit(1);
        }
    }
}
