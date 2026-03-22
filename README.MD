# ZO-Hash / DY-Hash

**⚠️ WARNING: This project contains self-developed hash algorithms that have not undergone cryptographic review. They contain severe security vulnerabilities and MUST NOT be used in production or any security-sensitive scenarios!**

This is an experimental Python module providing a custom 256‑bit hash algorithm (`Sponge256`) based on a sponge construction with ARX permutation, along with several encoding and fingerprint generation functions (`zo1`, `zo2`, `dy1`, etc.). The code is intended for learning, testing, or non‑adversarial use cases (e.g., detecting accidental file corruption).

---
## Other Languages
- # [中文](README_ZH.MD)

## Features

- `filehash_256v1` / `memoryhash_256v2` – self‑developed 256‑bit hash (not cryptographically validated)
- `zo_basev1` – ZO encoding of the hash (Base64‑like alphabet)
- `zo1` – hash + random sampled byte sum
- `zo2` – hash + file start/middle/end feature hash + random sampled byte sum
- `dy1` – fingerprint based on pseudo‑random bit‑sampling (64‑bit output)

All functions are deterministic – the same file always produces the same output.

---

## ⚠️ SECURITY WARNING (MUST READ)

### 1. Core Hash is Unverified
- The internal `Sponge256` is a completely self‑designed ARX permutation, **never cryptanalysed**.
- With only 12 rounds (or 24 in the “hardened” version), it may be vulnerable to differential/linear attacks.
- Any claim of “collision resistance” or “tamper‑proofness” is invalid.

### 2. Short Output & Linear Operations
- `dy1` produces only **64 bits** → birthday attack complexity is just \(2^{32}\). Collisions can be found in practice.
- `zo1` / `zo2` use simple byte‑wise summation (max ~32640) – attackers can adjust file content while keeping the sum unchanged.
- All final mixing (XOR, rotation) is linear, making algebraic attacks possible.

### 3. No Public Review
- The entire codebase has not been peer‑reviewed by the cryptographic community.
- Undisclosed vulnerabilities may exist: collision construction, preimage attacks, length‑extension, etc.

### 4. Prohibited Uses
- ❌ Digital signatures
- ❌ File integrity (anti‑tampering)
- ❌ Authentication
- ❌ Any security‑sensitive environment
- ❌ Production systems

### 5. Only Safe Use Cases
- ✅ Detecting accidental transmission errors (e.g., download checksums)
- ✅ Internal testing / experimental learning
- ✅ Non‑security identifiers when risks are fully understood (e.g., temporary cache keys)

---

## 🔍 Invitation for Security / Cryptographic Review

If you have experience in cryptography or hash function analysis, we warmly welcome your review of the code. Please point out specific vulnerabilities. Known weak spots include:

- `_hash.py` – `permutation` function (12/24 rounds ARX)
- `_zo.py` – `_file_sample_sum` (simple byte sum)
- `_dyhash.py` – `dy1` (64‑bit output + linear mixing)
- All functions that rely on the custom hash

**We welcome Issues and Pull Requests** that help improve the code or provide a detailed vulnerability analysis. If you find a practical collision attack, please let us know via an Issue.

---

## Installation

[code]
pip install zo-hash
[/code]

---

## Example Usage

[code]
from zohash import filehash_256v1, zo1, dy1

# File hash (256-bit integer)
h = filehash_256v1("example.txt")

# ZO1 fingerprint (string with checksum)
z = zo1("example.txt")

# DY1 fingerprint (64-bit, encoded as ZO string)
d = dy1("example.txt")
[/code]

---

## License

This project is provided for educational purposes only. Use at your own risk.