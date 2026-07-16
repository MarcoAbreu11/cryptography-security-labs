## Week 4 (24/02/2025) – Authenticated File Cipher

### Objective of the week
Improve the file cipher program from the previous week by adding integrity guarantees on top of confidentiality, through the combination of a symmetric cipher with a Message Authentication Code (MAC). Explore different approaches (encrypt-then-MAC, etc.) and authenticated encryption primitives (ChaCha20-Poly1305 and AES-GCM), using the `cryptography.hazmat` library. The requested programs were implemented, including demonstrations of CBC-MAC and password-based authenticated versions.

### 1. `cbc_mac.py` (PROG: cbc_mac.py)

CBC-MAC implementation with a fixed IV (all 'a'), using AES-256 (key adjusted to 32 bytes).

**Features:**
- `tag <key> <file>` → reads the file, applies zero padding if needed, computes the CBC encryption, extracts the last block (16 bytes) as the tag, and saves it to `<file>.tag`.
- `verify <key> <file> <tag>` → recomputes the tag the same way and compares it with the supplied one; raises `InvalidTag` if it does not match.

This version uses a fixed IV, which makes it insecure for variable-length messages (as explained in Q2).

### 2. `cbc_mac_rnd.py` (PROG: cbc_mac_rnd.py)

Improved version of CBC-MAC with a random IV (16 bytes via `os.urandom`), attempting to mitigate the security issues.

**Features:**
- `tag <key> <file>` → generates a random IV, computes the CBC-MAC, saves IV + tag (32 bytes) to `<file>.tag`.
- `verify <key> <file> <tag>` → extracts the IV from the tag file, recomputes the MAC with that IV, and verifies it.

Despite the random IV, it is still vulnerable to forgery attacks (see Q2).

### 3. `pbenc_aes_ctr_hmac.py` (PROG: pbenc_aes_ctr_hmac.py)

Password-based authenticated encryption program, using AES-CTR for confidentiality + HMAC-SHA256 for integrity (encrypt-then-MAC approach).

**Features:**
- `enc <ficheiro>` → prompts for a passphrase, generates a salt (16B), derives a key (32B) with PBKDF2 (SHA256, 1,200,000 iterations), splits it into key_enc (16B) + key_mac (16B), generates a nonce (16B), encrypts the content, computes an HMAC over the ciphertext, and saves salt + nonce + HMAC + ct to `<ficheiro>.enc`.
- `dec <ficheiro.enc>` → prompts for a passphrase, extracts salt/nonce/HMAC/ct, derives the key, verifies the HMAC over ct (fails with "Tags have changed!" if altered), decrypts, and saves the result to `.dec`.

This approach guarantees detection of any tampering with the ciphertext.

### 4. `pbenc_aes_gcm.py` (PROG: pbenc_aes_gcm.py)

Version using the authenticated AES-GCM primitive (a mode of operation that combines encryption and MAC internally).

**Features:**
- `enc <ficheiro>` → prompts for a passphrase and AAD (associated authenticated data), generates a salt (16B), derives a key (32B) with PBKDF2, generates a nonce (12B), encrypts with AESGCM (including the AAD in the authentication), and saves AAD_length (4B packed) + salt + AAD + nonce + ct/tag to `<ficheiro>.enc`.
- `dec <ficheiro.enc>` → extracts the components, derives the key, decrypts and verifies integrity (fails with "Wrong password or corrupted data" if invalid), saves the result to `.dec`.

AAD allows authenticating additional data without encrypting it.

### 5. `pbenc_chacha20_poly1305.py` (PROG: pbenc_chacha20_poly1305.py)

Similar to the previous one, but using ChaCha20-Poly1305 (an authenticated stream cipher primitive).

**Features:**
- `enc <ficheiro>` → prompts for a passphrase and AAD, generates a salt (16B), derives a key (32B) with PBKDF2, generates a nonce (12B), encrypts with ChaCha20Poly1305 (including the AAD), and saves AAD_length (4B packed) + salt + AAD + nonce + ct/tag to `<ficheiro>.enc`.
- `dec <ficheiro.enc>` → extracts the components, derives the key, decrypts and verifies (fails with "Error: wrong password or corrupted data"), saves the result to `.dec`.

Adapted from the previous week's sequential version to use authenticated encryption.

### Answers to the theoretical questions

**Q1 – What would be the impact of running the `chacha20_int_attck.py` program on a ciphertext produced by your program? Justify.**
The `chacha20_int_attck.py` program modifies the ciphertext by applying a delta (XOR) at specific positions, which would alter the decrypted plaintext. However, in this week's programs (e.g., `pbenc_aes_ctr_hmac.py`, `pbenc_aes_gcm.py` or `pbenc_chacha20_poly1305.py`), the ciphertext is protected by a MAC/tag. When decrypting a modified ciphertext:
- In encrypt-then-MAC (HMAC over ct), verification fails before decryption, raising "Tags have changed!".
- In GCM/Poly1305 modes, the integrated decryption fails with an integrity error ("corrupted data").
Thus, the tampering is detected, preventing the use of corrupted data — unlike the pure stream cipher from the previous week, where it would go unnoticed.

**Q2 – An attack on a MAC consists of, after obtaining valid message/tag pairs, being able to produce a new valid msg/tag pair without knowing the corresponding key. Show how it is possible to attack the version of the MAC that includes the random vector.**
The version with a random vector (`cbc_mac_rnd.py`) is still vulnerable due to the lack of a length prefix in the message and the use of zero padding.

Existential forgery attack (using a single valid pair):
1. Choose a message M of length l such that remainder = l % 16 ≠ 0 (e.g., l=15).
2. Compute the tag: random IV, padded_M = M + b'\x00' * (16 - remainder), tag = last block of CBC(IV, padded_M). Obtain the pair (M, IV + tag).
3. Forge a new message M' = M + b'\x00' * (16 - remainder), of length l' = l + (16 - remainder), which is a multiple of 16.
4. Use the same IV + tag for M'.

Justification: When verifying M', since l' % 16 = 0, no padding is added, so padded_M' = M' = M + 0^(16-remainder) = padded_M. The recomputed CBC is identical, so the tag matches. M' is different from M, but valid without knowing the key. This exploits the fact that the MAC is computed over the padded message without including the actual length, allowing equivalence between messages of different sizes.
