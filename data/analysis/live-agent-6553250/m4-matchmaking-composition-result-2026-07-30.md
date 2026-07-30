# M4 — resident matchmaking composition and drift

**Verdict: `NO_MATERIAL_MATCHMAKING_DRIFT`.** The newest opponent mix is not
demonstrably stronger or weaker in mean contemporaneous arena score than the oldest mix.
The panel does reveal strong version-lineage concentration that every future
matchmaking/opponent audit must preserve.

## Sources and endpoint design

- Exact resident: agent `6561795`.
- Processed corpus: 9,082 records, SHA-256
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  9,018 clean games, 241 resident games, 72 exact opponent identities.
- Current leaderboard: 2026-07-30T02:17:01Z, SHA-256
  `7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.
- Primary endpoints: the 60 oldest and 60 newest resident games by `gameId`; the middle
  121 games do not enter the endpoint contrast.
- Primary estimand: late minus early mean contemporaneous opponent `arenaScore`.
  Uncertainty uses 20,000 independent circular moving-block bootstraps (block length 10)
  and the exact 241-rotation temporal null.
- Terminal margin, win, duration, resources, and trajectory content are excluded from the
  drift verdict.

## Strength drift

| metric | oldest 60 | newest 60 | late − early |
|---|---:|---:|---:|
| mean opponent score | 22.297 | 22.735 | **+0.438** |
| median opponent score | 22.325 | 22.170 | **−0.155** |
| opponent-minus-resident mean gap | +0.117 | +0.555 | **+0.438** |

The primary mean-drift 95% CI is **[−0.865, +1.867]** and the exact circular-shift
two-sided p-value is **0.884**. Window-40 and window-80 estimates are +0.741 and +0.718;
seat-specific estimates are +0.500 and +0.420; every leave-one-exact-ID estimate remains
positive (+0.294 to +0.597). Those directional sensitivities do not rescue the primary
result: the +0.438 estimate misses the frozen 0.50 materiality gate, the CI crosses zero,
the temporal-null p-value fails, and the median moves in the opposite direction.

## Composition and version lineage

The endpoint distributions change sharply even though mean strength does not clear its
gate:

- exact identities contract from 38 to 16; effective exact-identity count from 31.58 to
  11.39;
- pseudonyms contract from 38 to **4**; effective pseudonym count from 31.58 to **1.58**;
- the newest 60 games are **47 FreZzz, 7 Bubaptik, 5 goq, and 1 IlyaPol**;
- all 60 newest games use exact IDs absent from the oldest endpoint, but only 6/60 use
  pseudonyms absent there;
- current-active exact-ID share falls from 91.7% to 21.7%, while current-active pseudonym
  lineage share remains 100% in both endpoints;
- 86.7% of newest games have opponent score 22–<24, versus 36.7% of oldest games; fixed
  score-bin Jensen–Shannon divergence is 0.337 bits.

Thus exact-ID inactivity mostly reflects superseded submissions, not disappearance of the
opponent lineage. Exact IDs remain mandatory for version-specific causal claims; pseudonym
lineages are mandatory for matchmaking concentration and longitudinal continuity.

Raw late-minus-early resident margin (−29.97) and win probability (−0.242) are retained
only as descriptive provenance. They cannot establish a matchmaking-strength effect or
mechanism and do not enter the verdict.

## Decision

Do not explain resident score/rank movement by a proven stronger matchmaking mix, and do
not create opponent-, lineage-, or composition-specific policy from M4. Update standing
surveillance to report both exact-ID and pseudonym-lineage concentration. Reopen material
strength drift only when the frozen mean, interval, temporal-null, median, window, seat,
and leave-one-out gates all pass on a later corpus.

Frozen protocol: `docs/m4-matchmaking-composition-protocol-2026-07-30.md`.
Machine bundle: `local_codex_1/m4-matchmaking-composition/`.

Artifact SHA-256:

- analyzer: `47ac0dd9ad0ab96bc05f80c321219ea16c73fab7254fc9df0553d71eb538e4b3`
- tests: `776c3a67052f318e7695015c67e72d2ec5e93e549115e8a28c932b647d04b286`
- `result.json`: `afdffc3b7e1408fa3b60a5f5961d92dde62d28cfd5421929d62e0ee8f11d6e02`
- `report.md`: `8e64fcd7c4c691f982e718ea30acaa425878f6e22240cfcea356ce93353a4243`
- `opponents.csv`: `c4ff1dc062b44216320542852e1274e488542a7cb5dd0c17c11675ac2b0c99ea`
