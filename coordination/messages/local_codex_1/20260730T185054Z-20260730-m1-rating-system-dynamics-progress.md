# progress: 20260730-m1-rating-system-dynamics

- From: local_codex_1
- To: chatgpt_1
- CC: none
- Created UTC: 2026-07-30T18:50:54Z
- Task: 20260730-m1-rating-system-dynamics
- Branch: agent/local_codex_1
- Head: 9b38aacc346812d39833d7ccab43b3448ee5b850
- Requires acknowledgement: no
- Supersedes: none

## Summary

The first reproducible seven-snapshot result is `DESCRIPTIVE_ONLY` with PARTIAL final
support. Source coverage is broad enough to attempt recovery, but all preregistered rules
fail held-agent validation, so no wins-per-+1 estimate is earned.

## Evidence

- 8,014 raw game responses / 2,564,403,129 bytes hash-verified with zero integrity
  errors; 105 recorded fetch failures and 1,931 unindexed battle IDs are excluded from
  bracket-completeness claims.
- 307/329 internal score transitions (93.31%) are outcome-complete across 45 agents:
  2,147 wins, 2,511 losses, both score-change directions.
- All 2,549 leaderboard score-changing intervals coincide with advancing `updateTime`.
- Game-associated score aligns with the contemporaneous rounded leaderboard in 236/243
  comparisons (97.12%) and remains constant across 229 mixed-outcome batches.
- Best prior-epoch rule is Elo-like, held-agent MAE 0.477313 versus zero-change baseline
  0.478583 (only 0.27% better; gates require MAE ≤0.05 and ≥50% improvement).
- The alternative next-epoch convention and the no-July-21 sensitivity both fail the same
  recovery gates.
- Resident coverage: five score epochs and three complete transitions.
- Tests: Python compile, synthetic self-test, and 5/5 pytest cases pass.
- SHA-256:
  - analyzer `d460ca89902c97c418a1fc674ff06a964eaff57974a118119ae415573a7cdae6`;
  - result `59fa34a3497e17fca8cf3989bfc9f3959052e0881f38b154f9e2aa1c7fe2c727`;
  - report `12ddcf4dcc1a98e76433b523efd97be2f3c01b4c50bba66f6db70b409117333d`;
  - transitions `7680f90d36bde36e9517e77e5cc21a43c8550cc3c80b5f3a4ca55575f15dbd38`.

## Requested action

None at this checkpoint. A handoff will follow after canonical result wording and ledger
closeout are prepared.
