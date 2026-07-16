# FCSI – Lab Assignments

This repository contains the practical assignment solutions developed for the **Fundamentos de Criptografia e Segurança da Informação (Fundamentals of Cryptography and Information Security)** course. Each week's folder includes the implementation, supporting files, and a report answering the corresponding theoretical questions.

## Overview

The assignments progress from classical ciphers to modern authenticated encryption, key exchange, digital signatures, X.509 certificates, and post-quantum cryptography, covering both the implementation of secure constructions and the practical exploitation of common vulnerabilities.

## Repository Structure

| Week | Topic | Folder |
|---|---|---|
| 01 | Introduction to the `cryptography` library / Unix `wc` emulation | [Guioes/S01](Guioes/S01) |
| 02 | Classical ciphers (Caesar, Vigenère) and the One-Time Pad | [Guioes/S02](Guioes/S02) |
| 03 | File encryption with ChaCha20 and stream cipher integrity attacks | [Guioes/S03](Guioes/S03) |
| 04 | Authenticated file encryption (CBC-MAC, AES-GCM, ChaCha20-Poly1305) | [Guioes/S04](Guioes/S04) |
| 05 | Padding Oracle Attack on AES-CBC | [Guioes/S05](Guioes/S05) |
| 06 | Simulation of security models (IND-CPA, IND-CCA, INT-PTXT) | [Guioes/S06](Guioes/S06) |
| 07 | Non-interactive Diffie-Hellman key exchange (NIKE) | [Guioes/S07](Guioes/S07) |
| 08 | Digital signatures (RSA) over the NIKE protocol | [Guioes/S08](Guioes/S08) |
| 09 | Use of X.509 certificates *(work in progress)* | [Guioes/S09](Guioes/S09) |
| 10 | Post-quantum cryptography: LWE-based KEM (FrodoKEM) | [Guioes/S10](Guioes/S10) |

Each folder contains:
- The original assignment statement (`S0X.md`);
- The corresponding source code / notebooks;
- A `README.md` with the solution write-up and answers to the theoretical questions.

## Technologies

- **Python 3**, primarily using the [`cryptography`](https://cryptography.io/) library (`cryptography.hazmat`) for symmetric and asymmetric primitives.
- **SageMath**, used in the lattice-based cryptography assignment (Week 10).
- **Jupyter Notebooks**, used where interactive exploration was required (Weeks 05, 06 and 10).

## Notes

- All reports were written by the group responsible for this repository as part of the FCSI course.
- Week 09 is currently marked as a work in progress; it will be completed and updated at a later date.

## Academic Context

- Course: Fundamentals of Cryptography and Information Security
- Degree: Computer Science
- University: University of Minho
- Academic year: 2025/2026
- Practical assignment's grade: 15/20
- Group Practical assignment's
