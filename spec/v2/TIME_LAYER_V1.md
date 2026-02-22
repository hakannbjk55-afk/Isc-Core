# TIME_LAYER_V1

## 1. Purpose

TIME_LAYER_V1 defines how temporal information is recorded and optionally anchored within an Evidence Pack.

This layer does not modify content hashing rules.
It augments existence claims with structured time metadata and optional external proofs.

The presence or absence of TIME_LAYER_V1 must not modify the core Evidence Pack hash.

---

## 2. Scope

This specification covers:

- Local time claim recording
- Optional RFC 3161 time stamp integration
- Optional OpenTimestamps (OTS) anchoring
- Offline verification rules

It does not define:

- Blockchain node operation
- TSA trust policy
- Long-term archival strategy

---

## 3. Data Model

TIME_LAYER_V1 consists of:

TIME_LAYER_V1
├── time_claim.local        (required)
├── time_proof.rfc3161      (optional)
└── time_proof.ots          (optional)

---

### 3.1 time_claim.local (REQUIRED)

Purpose:
Records the local system time observed at evidence generation.

Fields:

- iso8601_timestamp
- unix_epoch
- timezone_offset
- clock_source

Properties:

- Informational only
- Not a cryptographic proof
- Must always be present

Statement:

"This system observed this local time during evidence generation."

---

### 3.2 time_proof.rfc3161 (OPTIONAL)

Purpose:
Provides external time proof using an RFC 3161 Time Stamp Authority (TSA).

Requirements:

- Must cover the Evidence Pack hash or Merkle root
- Must validate cryptographically
- Must be verifiable offline using included certificate chain

Effect:

Establishes:
"The Evidence Pack hash existed at or before the TSA time."

Trust Model:
Depends on TSA key and certificate validity.

---

### 3.3 time_proof.ots (OPTIONAL)

Purpose:
Anchors Evidence Pack hash using OpenTimestamps.

Requirements:

- Must validate against referenced blockchain block
- Must be verifiable offline if block headers are available

Effect:

Establishes:
"The Evidence Pack hash existed before inclusion in the referenced blockchain block."

Trust Model:
Depends on public blockchain immutability.

---

## 4. Verification Rules

Verification must evaluate:

1) Evidence Pack hash integrity
2) Local time claim presence
3) RFC 3161 proof validity (if present)
4) OTS proof validity (if present)

Verification outcomes:

- VALID_LOCAL_ONLY
- VALID_RFC3161
- VALID_OTS
- INVALID

Multiple proofs may coexist.

---

## 5. Design Principles

- Local time is always recorded
- External anchoring is optional
- Core determinism must not be affected
- Verification must be reproducible
- Offline validation must be supported
