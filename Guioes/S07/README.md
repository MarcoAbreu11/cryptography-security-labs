# Week 7
## *Non-Interactive Diffie-Hellman Key-Exchange*

This repository contains the practical solution for **Assignment S07**, focused on implementing a non-interactive version of the *Diffie-Hellman* key agreement protocol. The goal is to demonstrate how to establish a session key asynchronously, using the recipient's public key, and apply it to authenticated encryption of a file.

## Objective

* **Non-Interactive Key Exchange (NIKE):** Implement a protocol where the sender (Alice) accesses the recipient's public key to establish a cipher without requiring a real-time exchange of messages.
* **Symmetric and Authenticated Encryption:** Use AES-GCM to ensure the confidentiality and integrity of the data during transfer.
* **Key Derivation (KDF):** Apply the HKDF algorithm with SHA-256 to turn the Diffie-Hellman shared secret into a strong cryptographic key.
* **Management and Serialization:** Handle the serialization of asymmetric key objects to/from files (PEM format) and manage variable-size data packets.

## Content and Implementation

The system logic is encapsulated in the `cfich_nike.py` file, which exposes a command-line interface with three main operations:

### 1. User Setup (`setup`)
Command: `python cfich_nike.py setup <user>`

This function is responsible for initializing a user's cryptographic identity:
* Creates finite field parameters using a predefined large prime number (p) and a generator (g = 2).
* Generates a *Diffie-Hellman* key pair (public and private).
* Stores the keys locally in the files `<user>.pk` and `<user>.sk` respectively, using `PEM` serialization.

### 2. Encryption and Packaging (`enc`)
Command: `python cfich_nike.py enc <user> <fich>`

To encrypt a message intended for a user (e.g., Bob):
* The application loads the recipient's public key from the `<user>.pk` file.
* Generates a new ephemeral *Diffie-Hellman* key pair for the sender (Alice) based on the same parameters.
* Performs the key agreement using the generated private key and the loaded public key, deriving a 32-byte session key via HKDF-SHA256.
* Encrypts the file's content using AES-GCM.
* The final ciphertext and Alice's public key are concatenated using the `mkpair` helper function (which includes length information to avoid parsing collisions). The result is saved with the `.enc` extension.

### 3. Decryption and Verification (`dec`)
Command: `python cfich_nike.py dec <user> <fich>`

To recover the original message:
* The function reads the content of the encrypted file and uses the `unpair` routine to extract the ephemeral public key (Alice's) and the ciphertext itself.
* Loads the user's private key from `<user>.sk`.
* Derives the same shared session key by combining its own private key with the ephemeral public key received in the packet.
* The ciphertext is validated and decrypted using AES-GCM. On success, the plaintext is written to a new file with the `.dec` extension.

## Mathematical Logic of the Protocol
In the classic key agreement, both parties openly exchange g^x (Alice) and g^y (Bob). The established symmetric key is defined as:

$$K = g^{(x \cdot y)}$$

In this **non-interactive** model, Bob publishes his g^y component in advance as his public key. When Alice wants to send a message, she generates an ephemeral secret x, computes and attaches her g^x (her own public key) to the encrypted message. Bob can then extract g^x from the packet and use his stored secret y to compute the key K, all without Alice needing to wait for an online response from Bob during the encryption process.
