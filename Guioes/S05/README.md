## Week 05: Padding Oracle Attack (CBC)

This week, we explored one of the most critical vulnerabilities in systems using block ciphers in CBC mode: the **Padding Oracle Attack**. The work focused on understanding how an attacker can use a server's (oracle's) error messages to decrypt data without possessing the encryption key.

All development was carried out in Python, using the `cryptography.hazmat` library to simulate the cryptographic environment.

### Summary of the Work Done

* **1. Study of PKCS7 Padding:**
  * Implementation of the `pad` and `unpad` functions for 128-bit blocks.
  * Verification of the redundancy introduced by padding: the value of each padding byte equals the total number of bytes added.

* **2. Solving Question 01 (Error Simulation):**
  * Demonstration that the *unpadding* error does not occur only due to incorrect block sizes, but also due to invalid bytes.
  * By removing just one byte from a correctly padded message (`unpad(pad(b"abc")[:15])`), the system raises a `ValueError: Invalid padding bytes`, providing the "hint" needed for the attack.

* **3. Implementation of the Padding Oracle (`pad_orcl`):**
  * Creation of a function that simulates a vulnerable server: it receives a ciphertext, decrypts it, and returns only `True` (if the padding is correct) or `False` (if it is incorrect).
  * This small information leak (the padding error being distinguishable from other errors) is the basis of the entire attack.

* **4. Discovering the Padding Length (`pad_orcl_attck_lastbyte`):**
  * Implementation of a function that manipulates the last block of the ciphertext to determine how many padding bytes the original message contains.
  * Through XOR operations on the second-to-last block, we force padding errors in the oracle until the exact padding position is determined.

* **5. Full Attack on the Last Block (`pad_orcl_attck`):**
  * Development of the iterative attack algorithm that recovers the plaintext byte by byte.
  * The attack manipulates the target byte and subsequent bytes (adjusting them to the target padding value, e.g. `0x01`, then `0x02`, etc.) and tests all 256 possible combinations until the oracle confirms success.
  * **Practical Result:** Successful recovery of the original message (e.g., `'Ola Mundo'`) without knowledge of the AES key.

---

### Attack Analysis

The success of this attack shows that **confidentiality (AES-CBC) without integrity (MAC)** is dangerous.
* The attacker does not need to break the AES cipher; they manipulate the Initialization Vector (IV) or the preceding block to change the outcome of decrypting the following block, using the unpadder's error as a guide.
* **Solution:** To mitigate this attack, authenticated encryption (AEAD) modes such as AES-GCM should be used, or the *Encrypt-then-MAC* approach should be applied, ensuring the padding is never checked if the MAC is invalid.
