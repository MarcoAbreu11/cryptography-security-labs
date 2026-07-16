# Week 10 — LWE KEM (FrodoKEM)

Implementation of the lattice-based public-key encryption (PKE) scheme **FrodoKEM**, developed as part of Week 10.

## Description
This assignment is dedicated to experimenting with a lattice-based (LWE) PKE scheme. The scheme is essentially FrodoKEM, adapted to allow for experimentation. The implementation was developed in **SageMath**, taking advantage of its native primitives for linear algebra over modular rings (`IntegerModRing`, `random_matrix`, `matrix`).

**FrodoKEM-640** (original parameters)
- $n = 640$, $q = 2^{15}$, $\bar{n} = 8$, $B = 2$, $\sigma \approx 2.8$

**miniFrodoKEM** (reduced parameters for experimentation)
- $n = 64$, $q = 2^{10}$, $\bar{n} = 8$, $B = 2$, $\sigma \approx 1.0$

## Implemented Tasks

1. **`genMat`** — Deterministic generation of the public matrix $A$ from a seed (`seedA`)
2. **`chiSample`** — Sampling from the $\chi$ distribution (Gaussian approximation) via a cumulative probability table
3. **`encode` / `decode`** — Encoding/decoding of 128-bit messages into $\bar{n} \times \bar{n}$ matrices
4. **Full PKE** — `keyGen`, `enc`, `dec` for FrodoKEM-640
5. **miniPKE** — Adaptation of the PKE for the reduced parameters
6. **Noise Impact Analysis** — Experiment with a noise distribution mismatched to the modulus $q$

## Results

| Scheme | $n$ | $q$ | $\sigma$ | Error rate |
|---|---|---|---|---|
| FrodoKEM-640 | 640 | $2^{15}$ | ≈ 2.8 | ≈ 0% |
| miniFrodoKEM (T_CHI64) | 64 | $2^{10}$ | ≈ 1.0 | ≈ 0% |
| miniFrodoKEM (T_CHI640) | 64 | $2^{10}$ | ≈ 2.8 | **≈ 100%** |

The last case illustrates how noise that is too large relative to a small modulus $q$ makes the scheme completely incorrect: the accumulated noise in the matrix multiplications exceeds the decoding threshold ($q / 2^{B+1} = 128$), making decryption impossible.
