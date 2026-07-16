# Week 8
## *Digital Signatures*

This repository contains the practical solution for **Assignment S08**, where the program used in the previous week's assignment was refined, with the goal of ensuring the authenticity of the parties involved (sender and recipient) by using RSA digital signatures.

## Objective

* **Authenticity of the Parties (RSA Digital Signatures):** Extend the previous NIKE protocol to guarantee not only confidentiality and integrity, but also the **authenticity** of the sender and recipient, using RSA digital signatures with PSS padding.

* **Hybrid Key Pair Management (DH + RSA):** Implement a setup system that generates and persists **four key files** per user — a DH pair (`<user>.dhpk` / `<user>.dhsk`) and an RSA pair (`<user>.rsask` / `<user>.rsapk`).

* **DH Public Key Authentication:** Ensure that a user's DH public key is **signed with RSA**, so that the `<user>.dhpk` file contains both the DH public key and its corresponding signature, preventing key substitution attacks.

* **Sign-then-Encrypt Cipher:** Apply the **sign first, encrypt after** paradigm — unlike the MAC applied after encryption in the previous assignment, the RSA signature is produced over the plaintext, and only afterward is the whole set encrypted.

* **Verification on Decryption:** During decryption, in addition to recovering the plaintext, **verify the sender's RSA signature**, returning an ERROR if validation fails — thus ensuring sender authenticity.

* **Unified Command-Line Interface:** Consolidate the three operations (`setup`, `enc`, `dec`) into a single program, `cfich_nikesig.py`, seamlessly integrating all DH and RSA key logic.

## Content and Implementation
The system logic is encapsulated in the `cfich_nikesig.py` file, which exposes a command-line interface with three main operations:

### 1. User Setup (`setup`)
Command: `python cfich_nikesig.py setup <user>`

This function is responsible for initializing a user's cryptographic identity:
* Creates finite field parameters using a predefined large prime number (p) and a generator (g = 2).
* Generates a *Diffie-Hellman* key pair (public and private).
* Generates an RSA key pair (public and private) of 2048 bits with public exponent 65537.
* **Signs the DH public key with the RSA private key**, using the PSS scheme with SHA-256, ensuring the authenticity of the DH public key.
* Saves the DH public key together with its RSA signature in the `<user>.dhpk` file (serialized with `mkpair`).
* Saves the DH private key, the RSA private key, and the RSA public key in the files `<user>.dhsk`, `<user>.rsask`, and `<user>.rsapk`, respectively, in `PEM` format.

### 2. Encryption and Signing (`enc`)
Command: `python cfich_nikesig.py enc <user> <me> <fich>`

To encrypt a message intended for a user (e.g., Bob), authenticating the sender (Alice):
* The application loads the `<user>.dhpk` file, extracting the recipient's DH public key and its corresponding RSA signature using `unpair`.
* Loads the recipient's RSA public key from `<user>.rsapk` and **verifies the signature of the DH public key**, aborting with an ERROR if validation fails.
* Generates a new ephemeral *Diffie-Hellman* key pair for the sender (Alice), based on the recipient's same parameters.
* Performs the key agreement using Alice's ephemeral private key and Bob's DH public key, deriving a 32-byte session key via HKDF-SHA256.
* Encrypts the file's content using AES-GCM.
* Following the **sign-then-encrypt** paradigm, **signs with RSA** (private key from `<me>.rsask`) the set formed by Alice's ephemeral public key concatenated with the ciphertext.
* The final result is packaged with `mkpair` (ephemeral public key + signature + ciphertext) and saved with the `.enc` extension.

### 3. Decryption and Verification (`dec`)
Command: `python cfich_nikesig.py dec <me> <user> <fich>`

To recover the original message and verify the sender's authenticity:
* The function reads the encrypted file and uses `unpair` to extract Alice's ephemeral public key, the RSA signature, and the ciphertext.
* Loads the sender's RSA public key from `<user>.rsapk` and **verifies the RSA signature** over the pair (ephemeral public key + ciphertext), aborting with an ERROR if validation fails.
* Loads the recipient's DH private key from `<me>.dhsk`.
* Derives the same shared session key by combining its own DH private key with the ephemeral public key received in the packet, via HKDF-SHA256.
* The ciphertext is validated and decrypted using AES-GCM. On success, the plaintext is written to a new file with the `.dec` extension.
