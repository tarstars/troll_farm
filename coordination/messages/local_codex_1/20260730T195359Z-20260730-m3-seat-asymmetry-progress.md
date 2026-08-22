# progress: 20260730-m3-seat-asymmetry

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:53:59Z
- Task: 20260730-m3-seat-asymmetry
- Branch: agent/local_codex_1
- Head: ae2100370014354d0df4b68d52b5e87af0d5731e
- Requires acknowledgement: no
- Supersedes: none

## Summary

Implementation lock ready. The source/count preflight reproduces 9,082 records, 9,018
clean games, 241 resident games, 72 exact opponents, and raw seat counts 126/115.

Primary same-exact-opponent matching supports 37 seat-1 targets across 23 identities. A
reduced-resample smoke run completes and gives a provisional seat-1-minus-seat-0 matched
margin of +10.088; the frozen full 20,000-bootstrap / 50,000-null run remains next.

## Evidence

- Analyzer SHA-256:
  `2c8003e1e18b24cd5143d8440ab727ecc630e3180f0b7e3b1a65dc405c2912c5`.
- Tests SHA-256:
  `4e585f1c8cdd71ca308e7dbdb6b560ddc152fb4d29cd02f06226763fa0451a38`.
- Compile and self-test pass; five focused tests pass.
- Tests cover exact identity/opposite-seat/pre-outcome matching, orientation reversal,
  deterministic cluster bootstrap/null, leave-one-cluster-out, and fixed-effect contrast.
- Resident remains byte-exact at SHA
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Requested action

None. Run the frozen full audit and report every support/actionability gate.
