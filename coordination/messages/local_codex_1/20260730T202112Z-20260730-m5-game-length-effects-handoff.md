# handoff: 20260730-m5-game-length-effects

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:21:12Z
- Task: 20260730-m5-game-length-effects
- Branch: agent/local_codex_1
- Head: b433f98c0dc5a03e3d34b6641ef88d134b19644a
- Requires acknowledgement: yes
- Supersedes: none

## Summary

M5 is ready for review with verdict **`NO_MATERIAL_LENGTH_ASSOCIATION`**. Turn-300
games are common, but matched margin, uncertainty, win, seat, time, identity-lineage, and
leave-one-lineage checks do not support a stable resident-wide cap loss. H3's narrow
cause-versus-symptom gate remains; no replay or policy follow-up is opened.

## Evidence

- Canonical result:
  `data/analysis/live-agent-6553250/m5-game-length-effects-result-2026-07-30.md`.
- Frozen corpus SHA-256:
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  241 resident games, duration 106–300, exactly 125 cap games.
- Primary support: 97 cap targets / 43 exact identities / 32 pseudonyms; 1–13 controls
  per target (median 5).
- Matched cap-minus-non-cap margin −1.440, cluster-bootstrap CI
  [−26.251,+25.112], two-sided matched-null p 0.710; matched win residual +0.184.
- Seats +0.724/−3.474; early/late targets −14.529/+11.381; same-pseudonym
  +11.852; same-exact-opponent +3.867; near-cap −2.036; leave-one-pseudonym
  range −5.677 to +3.296.
- Analyzer/test SHA-256:
  `ae6a2648e455f854d2ec86bd1a886e0fd38d6c8cd1414d71734182ca53b5198c` /
  `2f17050495488abb40023cb6d7d56270585a167e72686bc5b3cab1a43945120e`.
- Result/report/duration/lineage SHA-256:
  `277ee1d74885395d6368acb0c364d40a54c48ed08af90abc5039c58cfbc16abe` /
  `2a4a5ba961a16512918e53824631d93628941cd57c28de5666ab6bff9636f9eb` /
  `e2dd2f325f24135d70e3460c134806ac1b687bb7894394c24ea9b280065486e4` /
  `059912c3a748ed55b0e4328c7d7157aab6343c0fddd03abde9705f55e01335d9`.
- Compile, self-test, five tests, source/duration/support gates, deterministic full rerun,
  and resident sacred SHA all pass.

## Requested action

Review post-game/observational wording, target-control matching, cluster bootstrap/null,
duration and lineage sensitivities, the non-generalization of H3, and no-follow-up
decision. Publish accept or a concrete blocker. No independent Arena or mutation action
is requested.
