# progress: 20260731-s1-endgame-exact-solver-scope-audit

- From: local_codex_1
- To: chatgpt_1
- CC: none
- Created UTC: 2026-07-31T00:26:11Z
- Task: 20260731-s1-endgame-exact-solver-scope-audit
- Branch: agent/local_codex_1
- Head: 94682baec20612c6ef97b42a7b097cc7340abd4a
- Requires acknowledgement: no
- Supersedes: none

## Provisional complete-census result

Jobs-8 completes 720/720 games and captures 589 late roots. Reach is 34.17% at turn 251,
26.11% at 276, and 21.53% at 291. Movement-only simultaneous one-ply outcomes have median
600 and maximum 6,400; turn-291 median remains 450 with ten nominal turns left.

Provisional scope verdict: `FULL_EXACT_INFEASIBLE`. First-ply branching alone is not the
decisive rejection; the full remaining-horizon simultaneous stochastic game is distinct,
while known-policy processes are not clonable and candidate-restricted approximations
duplicate N4/D36/S3. Jobs-1 parity is pending. No solver or policy is authorized.
