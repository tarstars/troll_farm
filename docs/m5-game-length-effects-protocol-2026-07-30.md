# M5 — exact-resident game-length / turn-cap association protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T20:11:33Z
- Base commit: `396ca04fdb2cc0abb595b31b252dc96de25bca1b`
- Scope: current-corpus read-only duration/outcome audit; no replay, policy, or Arena work

## 1. Decision

Characterize exact-resident outcomes by recorded game length and determine whether games
reaching the 300-turn cap are materially associated with worse or better outcomes than
comparable shorter games. Return exactly one:

- `MATERIAL_CAP_LOSS_ASSOCIATION`: cap games are materially worse and every frozen
  support, uncertainty, outcome, and stability gate passes;
- `MATERIAL_CAP_GAIN_ASSOCIATION`: cap games are materially better and every gate passes;
- `NO_MATERIAL_LENGTH_ASSOCIATION`: support is adequate but the full gate does not pass;
- `UNIDENTIFIABLE`: source integrity or matched support fails.

Duration and reaching turn 300 are post-game variables, not randomized treatments.
No verdict may claim a causal turn-limit effect. A material association authorizes only
the H3-required read-only cause-versus-symptom replay audit; it does not authorize a
duration-conditioned policy, simulation, submission, TestSession, or Arena action.

## 2. Frozen source and support

Primary corpus:
`/home/tarstars/prj/troll_farm/data/processed/games.jsonl`, exactly 9,082 records,
game IDs 891153730–897326497, SHA-256
`12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`.

The exact resident is `agentId=6561795`. Preflight must reproduce 9,018 clean games, 241
clean resident games, 72 exact opponent identities, 126/115 raw seats, recorded duration
range 106–300, and exactly 125 turn-300 games.

The source does not provide a trusted referee terminal-reason label. `n_turns=300` means
only that the record reached the cap; it must not be relabeled timeout, stall, mercy, or
survival.

## 3. Raw duration characterization

Report counts, exact identities, seats, terminal margin, win indicator (1/0.5/0), own and
opponent final score, and pre-game strength for:

- 100–149 turns;
- 150–199;
- 200–249;
- 250–299;
- exactly 300.

Also report every observed exact duration, capped/non-capped quantiles, the non-cap
Spearman duration/margin association, and cap share by chronological half, seat, exact
identity, and pseudonym lineage. These are descriptive and cannot substitute for matched
gates.

## 4. Primary matched association

Primary targets are all turn-300 exact-resident games. For each target, eligible
non-cap controls satisfy:

- `n_turns < 300`;
- different opponent pseudonym from the target, avoiding same-lineage domination;
- same resident seat;
- exact same map width and height;
- opponent contemporaneous `arenaScore` within ±1.0;
- resident contemporaneous `arenaScore` within ±0.25;
- initial-tree count within ±4.

The target residual is its terminal margin minus the unweighted control-pool mean.
Secondary residual is the corresponding win-indicator difference. Targets are
equal-weighted. No terminal field except margin/win and no trajectory field may enter
control selection.

Primary support requires at least 80 supported cap targets from at least 30 exact target
identities, at least 30 supported targets in each resident seat, and at least 35 in each
chronological half. Preflight before outcome inspection finds 97 supported targets across
43 exact identities at the primary score band.

## 5. Uncertainty and sensitivities

Use deterministic seed `20260730`.

- Percentile 95% CI: 20,000 bootstraps resampling target exact-opponent clusters and
  retaining every supported target residual in each sampled cluster.
- Two-sided matched-null p-value: 50,000 replicates. For every target draw one margin from
  its control pool, subtract that pool mean, average across targets, and compare absolute
  values with the observed absolute mean using finite correction.
- Report leave-one-pseudonym-lineage-out primary estimates.

Frozen sensitivities:

1. opponent-score bands ±0.5 and ±1.5;
2. same-pseudonym matching instead of excluding the target pseudonym;
3. same-exact-opponent matching;
4. resident seat 0 and seat 1;
5. early and late chronological halves of supported targets;
6. controls restricted to 250–299 turns, reported as a near-cap comparison if support
   remains at least 30 targets / 15 identities;
7. raw cap-minus-non-cap association.

Same-pseudonym and exact-opponent estimates are support-limited sensitivities, not primary
substitutes.

## 6. Material-association gates

A cap-loss or cap-gain verdict requires all:

1. source and primary matched support pass;
2. absolute mean matched-margin residual ≥ **20 points**;
3. bootstrap 95% CI excludes zero;
4. two-sided matched-null p ≤ **0.05**;
5. matched win residual has the same sign and absolute magnitude ≥ **0.10**;
6. seat-0 and seat-1 residuals have the same sign;
7. early and late target-half residuals have the same sign;
8. identified ±0.5 and ±1.5 band residuals have the same sign;
9. same-pseudonym sensitivity has the same sign;
10. every leave-one-pseudonym-lineage-out estimate has the same sign.

There is no post-hoc relaxed threshold. Exact-opponent and near-cap results are reported
but are not gates because their support is not guaranteed. If primary support passes and
any gate fails, return `NO_MATERIAL_LENGTH_ASSOCIATION`.

## 7. Outputs and acceptance

Exclusive compact outputs:

- `cgauto/game_length_effects.py`;
- `tests/test_game_length_effects.py`;
- machine result, duration/lineage tables, and report under
  `local_codex_1/m5-game-length-effects/`;
- canonical result under
  `data/analysis/live-agent-6553250/m5-game-length-effects-result-2026-07-30.md`.

Acceptance commands:

```text
python3 -m py_compile cgauto/game_length_effects.py
python3 cgauto/game_length_effects.py --self-test
python3 -m pytest -q tests/test_game_length_effects.py
python3 cgauto/game_length_effects.py <recorded exact arguments>
```

The analyzer must verify the source hash/counts/duration support, sort outputs
deterministically, record every gate, and reproduce output hashes on a second full run.
The reviewer checks post-game-variable wording, control selection, cluster dependence,
sensitivities, and the H3 causal boundary.
