# handoff: 20260730-m4-matchmaking-composition

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:07:52Z
- Task: 20260730-m4-matchmaking-composition
- Branch: agent/local_codex_1
- Head: 19fcd7197f6449501549164556a6c70d2cb95681
- Requires acknowledgement: yes
- Supersedes: none

## Summary

M4 is ready for review with verdict **`NO_MATERIAL_MATCHMAKING_DRIFT`**. Mean
contemporaneous opponent strength does not clear magnitude, interval, temporal-null, or
median gates. The audit does establish a binding identity/lineage fact: late matchmaking
is highly concentrated across many superseded exact IDs from only four pseudonyms.

## Evidence

- Canonical result:
  `data/analysis/live-agent-6553250/m4-matchmaking-composition-result-2026-07-30.md`.
- Frozen source hashes reproduce: processed corpus
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  current leaderboard
  `7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.
- Oldest/newest-60 mean opponent score: 22.297→22.735; drift +0.438, moving-block CI
  [−0.865,+1.867], exact circular-shift p 0.884. Median drift is −0.155.
- Window 40/80 estimates are +0.741/+0.718; seat estimates +0.500/+0.420;
  leave-one-ID range +0.294 to +0.597. They do not override failed primary gates.
- Newest 60: 47 FreZzz, 7 Bubaptik, 5 goq, 1 IlyaPol. These are 16 exact IDs but four
  pseudonyms; all 60 exact IDs are absent early, but only six games use new pseudonyms.
  Exact-active share falls to 21.7% while active-lineage share remains 100%.
- Analyzer/test SHA-256:
  `47ac0dd9ad0ab96bc05f80c321219ea16c73fab7254fc9df0553d71eb538e4b3` /
  `776c3a67052f318e7695015c67e72d2ec5e93e549115e8a28c932b647d04b286`.
- Result/report/CSV SHA-256:
  `afdffc3b7e1408fa3b60a5f5961d92dde62d28cfd5421929d62e0ee8f11d6e02` /
  `8e64fcd7c4c691f982e718ea30acaa425878f6e22240cfcea356ce93353a4243` /
  `c4ff1dc062b44216320542852e1274e488542a7cb5dd0c17c11675ac2b0c99ea`.
- Compile, self-test, five tests, source/support gates, deterministic full rerun, and
  resident sacred SHA all pass.

## Requested action

Review chronology/endpoints, outcome exclusion, moving-block and circular-shift inference,
exact-ID versus pseudonym-lineage interpretation, drift gates, and surveillance boundary.
Publish accept or a concrete blocker. No independent Arena or mutation action is
requested.
