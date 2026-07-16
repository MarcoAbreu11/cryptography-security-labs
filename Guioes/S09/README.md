# Week 9
## *Using Certificates*

> **⚠️ Note:** This assignment is not yet complete. It will be finished at a later date.

This repository contains the practical solution for **Assignment S09**, whose goal is to introduce and manipulate X.509 digital certificates for identity validation and file signing.

## Objective

* **Use of X.509 Certificates:** Replace the manual, "blind" distribution of public keys with digital certificates, establishing key authenticity through a trusted third party.
* **Certificate Chain Validation:** Implement mechanisms that validate a certificate against a trust anchor (Certificate Authority - CA), checking the validity period, the issuer, and the applicable permissions (extensions such as *KeyUsage*).
* **Integrated Digital Signature:** Produce digital signatures (with RSA-PSS and SHA-256) over file content, attaching the signer's certificate to the result, ensuring that the verifier has access to the declared public key.
* **Two-Stage Verification:** During verification, first ensure that the attached certificate is authentic and valid (validating it against the trusted CA), and only afterward cryptographically verify the file's signature.

## Content and Implementation

The system logic is encapsulated in the `cfich_certs.py` file, which exposes a command-line interface with two main operations (signing and verification):

### 1. File Signing (`sign`)
Command: `python cfich_certs.py sign <ficheiro> <user>.key <user>.crt [password]`

This function is responsible for digitally signing a file and attaching the signer's certificate:
* Loads the user's private key from the `<user>.key` file (protected by a password, `b"1234"` by default).
* Loads the user's X.509 certificate from `<user>.crt`.
* Reads the full content of the `<ficheiro>` and generates a digital signature using the private key with the **RSA-PSS scheme and the SHA-256 hash function**.
* Writes the result to a new file `<ficheiro>.sig`, containing the certificate in PEM format, followed by a separator (`---SIGNATURE---`) and the Base64-encoded signature.

### 2. Signature and Certificate Verification (`verify`)
Command: `python cfich_certs.py verify <ficheiro> <CA>.crt`

To verify the authenticity and integrity of the signed file:
* The program reads the `<ficheiro>.sig` file, separating the signer's certificate from the signature itself.
* Loads the provided Certificate Authority (CA) certificate (`<CA>.crt`), which acts as the trust anchor.
* **Validates the Certificate:** Confirms whether the signer's certificate was directly issued by the CA, whether it is within its validity period, and whether it has the *KeyUsage* extension authorized for digital signatures. If the certificate is invalid, execution aborts.
* Reading the content of the original `<ficheiro>`, **verifies the RSA-PSS signature** using the public key contained in the previously validated certificate. Returns a success message if the signature matches, or an error otherwise.

---

## **Question: Q1**

To verify that the keys provided in the mentioned files form a valid RSA key pair, we can use the terminal commands `openssl x509 -text -noout -in xxx.crt` and `openssl rsa -text -noout -in xxx.key`, both present in the assignment, and observe in the output of both that the "modulus", where $modulus = p \times q$ with $p$ and $q$ prime, is the same in both the private and public keys, as can be verified in the `ALICE.key` and `ALICE.crt` files.

For an even more detailed and exhaustive check, one should verify whether the exponents "d" (private) and "e" (public) are multiplicative inverses of each other (invertible) in the corresponding modular ring.

Note that, to answer this question, we made use of artificial intelligence, specifically Gemini, to understand concepts such as *modulus* ($n = p \times q$) and its importance in linking the keys of an RSA pair.

## **Question: Q2**

In our view, the fields that require attention during the verification process are the following:

| Field  | Reason  |
| :---   | :---   |
| Issuer | Confirm that the CA is trusted |
| Subject | Confirm the holder's identity |
| Validity | Ensure it has not expired |
| Public Key Info | Confirm the associated public key |
| Signature Algorithm | Ensure secure algorithms are used |
| Key Usage | Confirm the certificate is used for the correct purpose |

## **Question: Q3**

We can trigger and illustrate errors in the `cfich_certs.py` application in the following ways:

- **In certificate validation:**
  - Try to verify the signature by passing the wrong trust anchor to the `verify` command (e.g., using a `FAKE_CA.crt` instead of the `CA.crt` that issued the signer's certificate). This will cause the `verify_directly_issued_by` function to fail.
  - Change the computer's system date to a year far in the past or far in the future, forcing the `cert_validtime` function to raise a `VerificationError` because the certificate is outside its validity period.

- **In signature validation:**
  - Modify the content of the original `<ficheiro>` (add a space or change a letter) after generating the signature (`<ficheiro>.sig`). When the application attempts to verify it, the RSA-PSS verification will fail and raise `InvalidSignature` because the file's hash no longer matches the encrypted one.
  - Open the `<ficheiro>.sig` file in a text editor and change one or more characters in the Base64-encoded block (below the separator). The mathematical verification of the signature with the public key will fail immediately.
