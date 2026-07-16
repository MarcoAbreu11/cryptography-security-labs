
## Week 3 (23/02/2026) – File Cipher with ChaCha20

### Objective of the week
Implement a file cipher based on the **ChaCha20** stream cipher (`cryptography.hazmat` library), exploring its confidentiality properties as well as its limitations in terms of integrity and authentication. Three programs were developed, each answering exactly what was requested in the assignment.

### 1. `cfich_chacha20.py` (PROG: cfich_chacha20.py)

Main program requested in the assignment.

**Implemented features:**
- `setup <fkey>` → generates a cryptographically secure 32-byte key (`os.urandom(32)`) and stores it in the given file.
- `enc <fich> <fkey>` → reads the original file, loads the key, generates a 16-byte nonce (`struct.pack("<Q", 0) + 8 random bytes`), encrypts with `algorithms.ChaCha20`, and saves the result to `<fich>.enc` (nonce + ciphertext).
- `dec <fich.enc> <fkey>` → extracts the nonce from the first 16 bytes, decrypts, and saves the plaintext to `<fich>.dec`.

The nonce is always unique per encryption (8 fixed counter bytes set to 0 + 8 random bytes), fulfilling the assignment's requirement that the nonce be stored alongside the ciphertext.

### 2. `chacha20_int_attack.py` (PROG: chacha20_int_attck.py)

Practical demonstration of the integrity attack on stream ciphers.

**How it works:**
- Receives: `<fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>`
- Reads the ciphertext as a `bytearray`.
- If the new string is shorter, pads it with spaces until it matches the original length.
- Computes delta = `ptxtAtPos XOR newPtxtAtPos` and applies it directly to the ciphertext starting at the given position.
- Saves the modified file as `<fctxt>.attck`.

This program allows altering any part of the plaintext (even without the attacker knowing the key) simply by modifying the ciphertext.

### 3. `pbenc_chacha20.py` (PROG: pbenc_chacha20.py)

Final version implementing **Password-Based Encryption** following the best practices indicated in the assignment.

**Features:**
- Removes the `setup` command and the separate key file.
- `enc <ficheiro>` → prompts for a passphrase via `input()`, generates a 16-byte salt, derives a key with `PBKDF2HMAC(SHA256, 1,200,000 iterations)`, encrypts with ChaCha20, and saves the result to `<ficheiro>.enc` in the format: `salt (16B) + fullnonce (16B) + ciphertext`.
- `dec <ficheiro.enc>` → prompts for a passphrase, extracts salt/nonce/ciphertext, derives the key, and writes the result to `.dec`. If an error occurs (e.g., a malformed file), it warns "Wrong password".

### Answers to the theoretical questions

**Q2 – What is the impact of using a fixed NONCE (e.g., all zeros)?**
A fixed nonce makes the cipher **deterministic** and extremely fragile:
- Same plaintext + same key → always the same ciphertext.
- Reusing a nonce with the same key enables the "two-time pad" attack: XOR-ing two ciphertexts reveals the XOR of their corresponding plaintexts, completely breaking confidentiality.
- In real scenarios (multiple files encrypted with the same key), the attack becomes trivial.
Therefore, the nonce must always be unique and unpredictable (as implemented in the programs).

**Q3 – Can the entire content of the file be tampered with by flipping a single bit of the ciphertext?**
**Yes.**
ChaCha20 is a synchronous stream cipher with no integrity mechanism whatsoever (no MAC). There is no diffusion: flipping a single bit in the ciphertext causes exactly the same bit flip at the corresponding position in the decrypted plaintext.

The `chacha20_int_attack.py` program demonstrates this in practice: knowing only a small part of the original plaintext and its position, an attacker can arbitrarily alter any section of the file without knowing the key and without the recipient detecting it.

---
