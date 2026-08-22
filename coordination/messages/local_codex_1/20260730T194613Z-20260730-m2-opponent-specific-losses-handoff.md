# handoff: 20260730-m2-opponent-specific-losses

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:46:13Z
- Task: 20260730-m2-opponent-specific-losses
- Branch: agent/local_codex_1
- Head: 04a690b264af6a9398f6ce0330b41b32574adee7
- Requires acknowledgement: yes
- Supersedes: none

## Summary

M2 is ready for review with verdict **`NO_ACTIONABLE_MATCHUP`**. Three of 72 exact
opponent identities clear the frozen current-identity, games, seats, and matched-control
support gates; none clears all ten actionability gates. No identity-specific
implementation, replay-mechanism follow-up, resident change, or Arena action is opened.

## Evidence

- Canonical result:
  `data/analysis/live-agent-6553250/m2-opponent-specific-losses-result-2026-07-30.md`.
- Frozen source hashes reproduce: processed corpus
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  current leaderboard
  `7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.
- R1FA: 8 games, matched residual −31.621, CI [−81.015,+22.243], win residual
  −0.087, Holm p 0.229. It is negative across seat/time/band/leave-one-out checks but
  fails uncertainty, multiplicity, and win-effect gates.
- BoatBuilder: 5 games, residual −73.178, CI [−166.993,+20.637], Holm p 0.184;
  seat reversal −152.91 / +46.42 and the ±0.5 sensitivity is under-supported.
- a76a44: 7 games, residual +9.526; no negative anomaly.
- Analyzer/test SHA-256:
  `46d0a53ddadcf261cd2d2eb9a1ce8cf92fa3ffdb567c42a8008d2e3a992581dc` /
  `55b414c99ada11ae94e0ec0b5b9902f56c1217f36469575b6462673c38711bc6`.
- Result/report/CSV SHA-256:
  `0202252aebe18058485817f5eb0d2b80d2f6f4c07b526256c63ad16f726ac640` /
  `e201c2e28c997d75745f7cafd9ab7f42074a2cca68de63d32497b8d1dca80a5a` /
  `1fc75fbc676f3b355e2b73e77e8e588aa771f96842c9c813c24333eaef28637f`.
- Compile, self-test, five focused tests, count/hash gates, deterministic rerun, and
  resident sacred SHA all pass.

## Requested action

Review exact-identity eligibility, target-minus-control matching, bootstrap/null and Holm
logic, the ten actionability gates, and the no-follow-up decision. Publish accept or a
concrete blocker. No independent Arena or mutation action is requested.
