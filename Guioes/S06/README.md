# Assignment 6 — Security Model Simulation

Implementation and animation of security games in Python, demonstrating vulnerabilities of cryptographic constructions through concrete adversaries.

## Structure

The framework is built on two abstract classes (`Cipher_`, `INDCPA_Adv`) from which all implemented ciphers and adversaries inherit.

## Implementations

### `indcpa.py` — IND-CPA Game
- **Identity Cipher** + obvious adversary → **100% success** (insecure by definition)
- **ChaCha20** + random adversary (`random.randint(0,1)`) → **~50% success** (secure, negligible advantage)

### `indcpa_attck.py` — AES-ECB Attack
ECB encrypts blocks independently and deterministically: identical plaintext blocks produce identical ciphertext blocks. The adversary submits `m0 = AA` and `m1 = AB` and detects the repetition in the ciphertext → **100% success**.

### IND-CCA — Malleability of AES-CTR
CTR is malleable: XOR-ing a byte of the ciphertext produces the same XOR in the plaintext. The adversary modifies the challenge, decrypts it via the oracle, and undoes the change — recovering the plaintext without knowing the key → **100% success**.

### INT-PTXT — Simple Hash as MAC
`enc(m) = SHA256(m) || m` uses no key and provides no confidentiality. The adversary computes `SHA256(m0)` locally and compares it with the prefix of the challenge → **100% success**.

## Results

| Construction | Model | Success | Conclusion |
|---|---|---|---|
| Identity Cipher | IND-CPA | 100% | Insecure |
| ChaCha20 | IND-CPA | ~50% | Secure |
| AES-ECB | IND-CPA | 100% | Insecure (no diffusion) |
| AES-CTR | IND-CCA | 100% | Malleable (no MAC) |
| Simple Hash | INT-PTXT | 100% | Keyless MAC |
