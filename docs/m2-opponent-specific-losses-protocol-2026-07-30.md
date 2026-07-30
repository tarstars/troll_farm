# M2 — opponent-specific systematic-loss audit protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T19:35:48Z
- Base commit: `a4890910e4173a3114497e313052d2d5c99483d2`
- Scope: current-corpus read-only matchup audit; no replay mechanism work or Arena action

## 1. Decision

Determine whether the exact resident loses materially more than its own comparable-game
baseline against any currently active exact opponent identity. Return exactly one verdict:

- `ACTIONABLE_MATCHUP_ANOMALY`: at least one exact opponent passes every support,
  matching, multiplicity, value, and stability gate below;
- `NO_ACTIONABLE_MATCHUP`: the audit is adequately powered for at least one active
  repeated opponent, but none passes all gates;
- `UNIDENTIFIABLE`: no active repeated opponent has adequate support/matched controls or
  source integrity fails.

An anomaly authorizes only a new read-only replay/mechanism task. It does not authorize a
policy change, opponent-name branch, simulation, submission, TestSession, or Arena action.

## 2. Frozen sources and identity

Primary corpus:
`/home/tarstars/prj/troll_farm/data/processed/games.jsonl`, exactly 9,082
newline-delimited records, game IDs 891153730–897326497, SHA-256
`12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`.

Current activity/identity snapshot:
`/home/tarstars/prj/troll_farm/data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json`,
SHA-256
`7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.

Resident identity is exact `agentId=6561795`. Opponents are primary-keyed by exact
`agentId`; `pseudo` is presentation metadata and a preregistered lineage sensitivity only.
The source preflight must reproduce 9,018 clean games, 241 clean resident occurrences, and
72 distinct exact resident opponents. Any mismatch stops the audit.

Use each processed game's contemporaneous `players[].arenaScore`, not the later leaderboard
score, as the strength-matching variable. The current leaderboard is used only to decide
whether the exact target agent remains active and to report current rank/score.

## 3. Inclusion and outcomes

A clean game is exactly `cgauto.roster_outcome_pricing.is_clean`. The primary resident
panel contains every clean occurrence of exact resident `6561795`; no outcome, opponent,
duration, or roster filter is allowed.

Primary outcome: resident terminal score margin. Secondary outcome: resident win indicator
(1 win, 0.5 tie, 0 loss). Report raw score components descriptively, but do not use them
to construct expected outcomes.

Primary exact-opponent eligibility:

1. at least five resident games;
2. at least two resident games in each seat;
3. exact opponent `agentId` present in the frozen current leaderboard;
4. nonmissing contemporaneous scores and map features in every included game;
5. every target game has at least ten primary matched controls.

Report all 72 exact identities, including ineligible reasons. Aggregate same-`pseudo`
lineages only as sensitivity; a pseudonym must never substitute for exact identity in the
primary result.

## 4. Expected-outcome estimator

M1 did not recover a rating formula, so M2 must not fabricate Elo probabilities or a
wins-per-rating conversion. Expected outcome is the resident's own matched-game baseline.

For each target game, eligible controls are other clean resident games satisfying all:

- control opponent exact `agentId` differs from the target;
- control opponent `pseudo` differs from the target pseudo, excluding same-account/version
  contamination;
- same resident seat;
- exact same map width and height;
- absolute control-vs-target opponent contemporaneous `arenaScore` difference ≤1.0;
- absolute control-vs-target resident contemporaneous `arenaScore` difference ≤0.25;
- absolute initial-tree-count difference ≤4.

The target-game expected margin/win is the unweighted mean of its matched controls. Its
residual is observed minus expected. The opponent estimand is the unweighted mean across
target games, so no game with a large control pool gets extra weight.

Primary predictors/matches are all pre-game or identity/collection metadata. Final roster,
game length, final inventory, actions, trajectories, and terminal scores other than the
outcome itself are forbidden as adjustment variables.

## 5. Uncertainty, multiplicity, and sensitivities

Use deterministic seed `20260730`.

- Percentile 95% confidence interval: 20,000 opponent-game cluster bootstrap resamples of
  the target residual vector.
- One-sided matched-null Monte Carlo p-value: 50,000 replicates. For each target game draw
  one margin from its matched-control pool and subtract that pool's mean; average across
  target games. Use `(1 + null <= observed)/(B + 1)`.
- Apply Holm correction across all primary-eligible exact opponents. The family is frozen
  before seeing residuals.
- Repeat the estimator at opponent-score bands ±0.5 and ±1.5. A sensitivity is identified
  only if every target game retains at least ten controls.
- Split each target by resident seat and chronologically at its median game ID. Each
  required half must contain at least two games.
- Same-pseudo aggregation reports whether version lineage changes the conclusion; it is
  never a primary pass substitute.
- Report leave-one-game-out opponent residual range to expose single-game leverage.

## 6. Actionability gates

An exact opponent is actionable only if all are true:

1. primary eligibility passes;
2. mean margin residual ≤ **−20**;
3. bootstrap 95% upper confidence bound < **0**;
4. Holm-adjusted one-sided p ≤ **0.05**;
5. mean win residual ≤ **−0.15**;
6. both seat-specific mean margin residuals are negative;
7. both chronological-half mean margin residuals are negative;
8. both identified ±0.5 and ±1.5 score-band sensitivities are negative;
9. leave-one-game-out residual remains negative for every omission;
10. exact opponent remains present in the frozen current leaderboard.

Name every failed gate. Multiple actionable opponents are ranked by adjusted p, mean margin
residual, then exact agent ID. There is no post-hoc relaxed gate.

## 7. Outputs and acceptance

Exclusive compact outputs:

- `cgauto/opponent_specific_losses.py`;
- `tests/test_opponent_specific_losses.py`;
- machine result, per-opponent table, and report under
  `local_codex_1/m2-opponent-specific-losses/`;
- canonical result under
  `data/analysis/live-agent-6553250/m2-opponent-specific-losses-result-2026-07-30.md`.

Acceptance commands:

```text
python3 -m py_compile cgauto/opponent_specific_losses.py
python3 cgauto/opponent_specific_losses.py --self-test
python3 -m pytest -q tests/test_opponent_specific_losses.py
python3 cgauto/opponent_specific_losses.py <recorded exact arguments>
```

The analyzer must verify both source hashes, reproduce the frozen counts, sort outputs
deterministically, and record every eligibility/actionability gate. The reviewer checks
identity, outcome-free matching, control-pool construction, multiplicity, stability, and
the follow-up boundary.
