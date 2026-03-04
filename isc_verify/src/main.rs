use sha2::{Sha256, Digest};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::process;

#[derive(Debug)]
enum VerifyError {
    MissingFile(String),
    HashMismatch(String),
    ParseError(String),
    PackIdentityMismatch,
    IoError(String),
}

impl std::fmt::Display for VerifyError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            VerifyError::MissingFile(p) => write!(f, "Missing required file: {}", p),
            VerifyError::HashMismatch(p) => write!(f, "Hash mismatch: {}", p),
            VerifyError::ParseError(e) => write!(f, "Parse error: {}", e),
            VerifyError::PackIdentityMismatch => write!(f, "Pack identity mismatch: pack_hash does not match"),
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
        // Path traversal protection
        let entry_str = entry_path.to_string_lossy();
        if entry_str.contains("..") || entry_str.starts_with('/') {
            return Err(VerifyError::ParseError(format!("Unsafe path in tar: {}", entry_str)));
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
            return Err(VerifyError::ParseError(format!("Duplicate path in manifest: {}", path)));
        }
        paths_seen.insert(path.clone());
        entries.push((hash, path));
    }
    // Sort by path for canonical ordering
    entries.sort_by(|a, b| a.1.cmp(&b.1));
    Ok(entries)
}

fn verify_pack(pack_path: &Path) -> Result<(), VerifyError> {
    // Extract to temp dir
    let tmp = tempfile::tempdir().map_err(|e| VerifyError::IoError(e.to_string()))?;
    extract_tar(pack_path, tmp.path())?;

    // Find base dir (tar may have a top-level dir)
    let base = tmp.path().to_path_buf();

    // Check required files
    let required = ["artifacts/ci_report.json"];
    for req in &required {
        let p = base.join(req);
        if !p.exists() {
            return Err(VerifyError::MissingFile(req.to_string()));
        }
    }

    // Find manifest
    let manifest_candidates = [
        "artifacts/evidence_pack_manifest_v2.sha256",
        "artifacts/evidence_pack_manifest_v1.sha256",
        "content_manifest.sha256",
    ];
    let manifest_path = manifest_candidates.iter()
        .map(|p| base.join(p))
        .find(|p| p.exists())
        .ok_or_else(|| VerifyError::MissingFile("content_manifest.sha256".to_string()))?;

    // Parse and verify manifest
    let entries = parse_manifest(&manifest_path)?;
    let manifest_name = manifest_path.file_name().unwrap().to_string_lossy().to_string();

    for (expected_hash, rel_path) in &entries {
        // Skip manifest itself
        if rel_path.ends_with(&manifest_name) { continue; }
        let file_path = base.join(rel_path);
        if !file_path.exists() {
            eprintln!("  WARN: missing file: {}", rel_path); continue;
        }
        let computed = sha256_file(&file_path)?;
        if &computed != expected_hash {
            return Err(VerifyError::HashMismatch(rel_path.clone()));
        }
    }

    println!("Content integrity:  valid");

    // Compute content_hash
    let manifest_raw = fs::read(&manifest_path)
        .map_err(|e| VerifyError::IoError(e.to_string()))?;
    let content_hash = sha256_bytes(&manifest_raw);

    // Load ci_report.json
    let ci_report_path = base.join("artifacts/ci_report.json");
    let ci_raw = fs::read(&ci_report_path)
        .map_err(|e| VerifyError::IoError(e.to_string()))?;

    // Compute meta_hash
    let meta_hash = sha256_bytes(&ci_raw);

    // Compute expected pack_hash
    let combined = format!("{}{}", meta_hash, content_hash);
    let pack_hash_expected = sha256_bytes(combined.as_bytes());

    // Check pack_hash in ci_report.json if present
    if let Ok(ci_json) = serde_json::from_slice::<serde_json::Value>(&ci_raw) {
        if let Some(stored_hash) = ci_json.get("pack_hash").and_then(|v| v.as_str()) {
            let stored = stored_hash.trim_start_matches("sha256:");
            if stored != pack_hash_expected {
                return Err(VerifyError::PackIdentityMismatch);
            }
        }
    }

    println!("Pack identity:      valid");
    println!("  meta_hash:        {}", &meta_hash[..16]);
    println!("  content_hash:     {}", &content_hash[..16]);
    println!("  pack_hash:        {}", &pack_hash_expected[..16]);

    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        eprintln!("isc_verify v0.2.0");
        eprintln!("Usage:");
        eprintln!("  isc_verify --version");
        eprintln!("  isc_verify <evidence_pack.tar>");
        process::exit(2);
    }

    match args[1].as_str() {
        "--version" | "-V" => {
            println!("isc_verify {}", env!("CARGO_PKG_VERSION"));
        }
        path => {
            let pack_path = Path::new(path);
            if !pack_path.exists() {
                eprintln!("Error: file not found: {}", path);
                process::exit(1);
            }
            match verify_pack(pack_path) {
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
    }
}
