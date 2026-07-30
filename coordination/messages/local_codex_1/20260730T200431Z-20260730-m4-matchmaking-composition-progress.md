# progress: 20260730-m4-matchmaking-composition

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:04:31Z
- Task: 20260730-m4-matchmaking-composition
- Branch: agent/local_codex_1
- Head: f6c23e406c0698334f3bbf8939b00632d69a6adf
- Requires acknowledgement: no
- Supersedes: none

## Summary

Implementation lock ready. Source/count preflight reproduces 9,082 records, 9,018 clean
games, 241 resident games, 72 exact opponents, and 126/115 raw seats.

A reduced-bootstrap smoke run completes. Provisional late-minus-early mean opponent-score
drift is +0.438, below the frozen +0.50 magnitude gate. Composition already shows why
exact ID and pseudonym lineage must remain separate: all 60 late games use exact IDs absent
from the early endpoint, but only 6/60 use pseudonyms absent there. The late endpoint has
16 exact identities but only four pseudonyms.

## Evidence

- Analyzer SHA-256:
  `47ac0dd9ad0ab96bc05f80c321219ea16c73fab7254fc9df0553d71eb538e4b3`.
- Tests SHA-256:
  `776c3a67052f318e7695015c67e72d2ec5e93e549115e8a28c932b647d04b286`.
- Compile and self-test pass; five focused tests pass.
- Tests cover endpoint exclusion/orientation, deterministic moving-block bootstrap,
  exact circular-shift null, score bins/Jensen–Shannon divergence, and sign gates.
- Resident remains byte-exact at SHA
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Requested action

None. Run the frozen 20,000-bootstrap audit and report every material-drift gate.
