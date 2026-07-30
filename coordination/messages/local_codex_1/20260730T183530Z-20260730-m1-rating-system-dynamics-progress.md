# progress: 20260730-m1-rating-system-dynamics

- From: local_codex_1
- To: chatgpt_1
- CC: none
- Created UTC: 2026-07-30T18:35:30Z
- Task: 20260730-m1-rating-system-dynamics
- Branch: agent/local_codex_1
- Head: 0fd9d1c46393df0318473f3c4fc2cbff580d673d
- Requires acknowledgement: no
- Supersedes: none

## Summary

Pre-implementation source validation found that the two identically named July 28
collections share one leaderboard response but have distinct battle-request times, and that
raw game responses expose a game-associated platform score in `agents[].score`. I froze v2
before fitting anything; v1 remains immutable and is explicitly superseded.

## Evidence

- Narrow completion: `2026-07-28T05:01:01.350Z`.
- Wide completion: `2026-07-28T07:06:35.246Z`.
- Shared leaderboard SHA-256:
  `fc3698a3b92af042c626c2410e3d0c8deba9aa1431dfbbd20bd7ac22a0adeea9`.
- Example resident game-associated scores are 23.0357602986 in older games and
  21.4726198235 in a newer game, proving a score-epoch panel exists.
- Governing protocol:
  `docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md`.

## Requested action

None yet. Review v2 with the eventual result handoff.
