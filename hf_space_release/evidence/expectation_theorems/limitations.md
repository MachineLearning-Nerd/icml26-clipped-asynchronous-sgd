# Claims 1–2 limitations

- This is a machine-checked symbolic derivation with an explicit trusted rule
  set, not a Lean, Coq, or Isabelle kernel proof.
- Soft-O hides logarithms and constants depending on fixed `L`, `Delta`, and
  `theta`; the certificate exposes where they enter.
- The proof repairs several presentation errors in the printed appendix and
  lists each repair. It does not silently treat the printed algebra as valid.
- The certificate verifies the expectation theorems only. It makes no claim
  about the separate high-probability rates.
