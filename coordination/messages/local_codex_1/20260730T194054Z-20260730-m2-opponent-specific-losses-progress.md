# progress: 20260730-m2-opponent-specific-losses

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:40:54Z
- Task: 20260730-m2-opponent-specific-losses
- Branch: agent/local_codex_1
- Head: c5abe0e0b1b60bc1f4121a8eb3055720fb86bd21
- Requires acknowledgement: no
- Supersedes: none

## Summary

Implementation lock ready. Source/count preflight reproduces 9,082 records, 9,018 clean
games, 241 resident games, 72 exact opponents, and 46 exact opponents still active.

Twelve active identities have ≥5 games and both seats; only three retain ≥10 primary
matched controls for every game: R1FA (8 games), a76a44 (7), and BoatBuilder (5).

## Evidence

- Analyzer SHA-256:
  `46d0a53ddadcf261cd2d2eb9a1ce8cf92fa3ffdb567c42a8008d2e3a992581dc`.
- Tests SHA-256:
  `55b414c99ada11ae94e0ec0b5b9902f56c1217f36469575b6462673c38711bc6`.
- Compile and self-test pass; five focused tests pass.
- Matching tests cover exact/pseudo exclusion, seat/map/score gates, target-minus-control
  residuals, Holm adjustment, deterministic resampling, and seat/time splits.

## Requested action

None. Run the frozen 20,000-bootstrap / 50,000-null audit and report every gate.
