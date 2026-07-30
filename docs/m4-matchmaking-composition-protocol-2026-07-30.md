# M4 — resident matchmaking-composition audit protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T19:59:19Z
- Base commit: `25dce522ecab58fca111d2550863aa6bdd571d2b`
- Scope: current-corpus read-only composition/drift audit; no replay, policy, or Arena work

## 1. Decision

Characterize who the exact resident plays, how concentrated that mix is, and whether the
newest opponent-strength mix differs materially from the oldest mix. Return exactly one:

- `MATERIAL_STRONGER_OPPONENT_DRIFT`: the late opponent mix is materially stronger and
  every frozen drift gate passes;
- `MATERIAL_WEAKER_OPPONENT_DRIFT`: the late opponent mix is materially weaker and every
  frozen drift gate passes;
- `NO_MATERIAL_MATCHMAKING_DRIFT`: source/support are adequate but the full drift gate
  does not pass;
- `UNIDENTIFIABLE`: source integrity or endpoint support fails.

A material result updates longitudinal score/maturity interpretation and surveillance
only. It does not authorize opponent-specific behavior, resident changes, simulation,
submission, TestSession, or Arena action.

## 2. Frozen sources and identity

Primary corpus:
`/home/tarstars/prj/troll_farm/data/processed/games.jsonl`, exactly 9,082 records,
game IDs 891153730–897326497, SHA-256
`12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`.

Current identity/activity snapshot:
`/home/tarstars/prj/troll_farm/data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json`,
SHA-256
`7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.

The exact resident is `agentId=6561795`. Preflight must reproduce 9,018 clean games, 241
clean resident occurrences, 72 exact resident opponents, and raw seats 126/115. Use
processed-game `players[].arenaScore` as the contemporaneous strength field. The current
leaderboard is presentation/activity metadata only.

`agentId` is the primary identity; `pseudo` is a lineage summary. Chronology is ordered by
`gameId`, then source record index. No wall-clock timestamp is inferred from game IDs.

## 3. Frozen endpoint comparison

Primary endpoint windows are the 60 oldest and 60 newest exact-resident games. The middle
121 games are excluded from the endpoint contrast but retained for full-panel composition
and trend summaries.

Primary estimand: late minus early mean contemporaneous opponent `arenaScore`.
Secondary composition estimands:

- late minus early median opponent score;
- late minus early mean `(opponent arenaScore − resident arenaScore)` gap;
- fractions with opponent score below the resident by more than 0.5, within ±0.5, and
  above the resident by more than 0.5;
- exact-identity and pseudonym frequencies, unique counts, HHI, effective identity count,
  repeat share, late identities absent from the early window, and current-active share;
- fixed score bins `<20`, `20–<22`, `22–<24`, `24–<26`, `≥26`, with Jensen–Shannon
  divergence between endpoint distributions;
- seat, map-dimension, initial-tree, and contemporaneous resident-score composition.

Terminal margin, win rate, game length, final resources, and trajectory fields are
forbidden from the drift verdict. Margin and win may be reported in a clearly descriptive
section only.

## 4. Uncertainty and temporal null

Use deterministic seed `20260730`.

- Percentile 95% CI: 20,000 independent endpoint moving-block bootstraps. Sample circular
  contiguous blocks of length 10 within each 60-game endpoint until 60 observations are
  filled, then compute late minus early mean opponent score.
- Temporal-null p-value: exact circular shifts of the full 241-game chronological opponent
  score sequence. For all 241 rotations, recompute the two 60-game endpoint means; report
  the finite exact two-sided fraction whose absolute difference is at least the observed
  absolute difference.
- Report ordinary least-squares slope of opponent score against normalized resident-game
  ordinal and Spearman rank correlation descriptively; neither substitutes for endpoint
  gates.

## 5. Frozen sensitivities

Repeat mean/median/gap endpoint contrasts at window sizes 40 and 80. Also report:

1. exact identities only versus same-pseudo lineages;
2. active-current opponents only, without treating inactivity as evidence of weakness;
3. seat-0 and seat-1 endpoint contrasts separately;
4. leave-one-exact-opponent-out primary mean-drift range;
5. first-half versus second-half mean opponent score as a lower-resolution check.

## 6. Material-drift gates

A stronger or weaker drift verdict requires all:

1. source and endpoint support pass (241 resident games and 60/60 endpoints);
2. absolute primary mean opponent-score drift ≥ **0.50**;
3. block-bootstrap 95% CI excludes zero;
4. exact circular-shift two-sided p ≤ **0.05**;
5. median opponent-score drift has the same sign and absolute magnitude ≥ **0.25**;
6. opponent-minus-resident score-gap drift has the same sign;
7. window-40 and window-80 mean drifts have the same sign and absolute magnitude ≥
   **0.25**;
8. both seat-specific endpoint mean drifts are identified and have the same sign;
9. every leave-one-exact-opponent-out primary estimate has the same sign.

There is no post-hoc relaxed threshold. If support passes but any gate fails, return
`NO_MATERIAL_MATCHMAKING_DRIFT`.

## 7. Outputs and acceptance

Exclusive compact outputs:

- `cgauto/matchmaking_composition.py`;
- `tests/test_matchmaking_composition.py`;
- machine result, opponent table, and report under
  `local_codex_1/m4-matchmaking-composition/`;
- canonical result under
  `data/analysis/live-agent-6553250/m4-matchmaking-composition-result-2026-07-30.md`.

Acceptance commands:

```text
python3 -m py_compile cgauto/matchmaking_composition.py
python3 cgauto/matchmaking_composition.py --self-test
python3 -m pytest -q tests/test_matchmaking_composition.py
python3 cgauto/matchmaking_composition.py <recorded exact arguments>
```

The analyzer must verify both hashes and all frozen counts, sort output deterministically,
record every drift gate, and reproduce output hashes on a second full run. The reviewer
checks chronology, endpoint exclusion, contemporaneous strength, temporal inference,
identity lineage, uncertainty, and the no-policy boundary.
