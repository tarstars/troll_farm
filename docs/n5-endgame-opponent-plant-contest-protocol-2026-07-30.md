# N5 — endgame opponent-plant contest audit protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T20:30:00Z
- Base commit: `50eca900a2edcc669f29b05b99781e8e113839ec`
- Scope: current-corpus read-only generation-lineage audit; no simulation, policy, or Arena work

## 1. Decision and causal boundary

Quantify the replay-observed opportunity associated with the published design's missing
endgame instruction to park near the opponent shack and contest last-minute planting.
Return exactly one:

- `MATERIAL_CONTEST_OPPORTUNITY`: the conservative, replay-conditioned resident
  opportunity clears the frozen 20-margin gate with adequate support and integrity;
- `NO_MATERIAL_CONTEST_OPPORTUNITY`: support and integrity pass, and the upper confidence
  limit remains below 20 margin per resident game;
- `UNIDENTIFIABLE`: support/integrity fails or the confidence interval overlaps 20.

This is an observational audit of realized replays. It cannot identify the causal value
of adding a policy, because different positioning would change both players' later
actions and generation yield. `MATERIAL_CONTEST_OPPORTUNITY` authorizes only a separately
frozen controlled-simulation proposal. No verdict authorizes source changes, simulation,
submission, TestSession, or Arena action.

Enemy units can share cells. Therefore "contest" never means body-blocking. It means
being positioned to HARVEST or CHOP a newly planted opponent generation on later turns.

## 2. Frozen source

Use the logical repository paths below from the host worktree containing the replay
corpus:

- `data/processed/games.jsonl`: 9,082 records, game IDs 891153730–897326497,
  SHA-256 `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
- `data/raw/games/<gameId>.json`;
- `data/processed/trajectories/<gameId>.jsonl`.

The exact subject cohorts are:

- resident `agentId=6561795`: 242 indexed games, sorted-ID-list SHA-256
  `3ea12d776e10019905b098ca159b4688266fe6874935a7d03c58ce216b8ec91c`;
- yamo `agentId=6479814`: 140 indexed games, sorted-ID-list SHA-256
  `0dc44b60be9e6ed893cc0226b3e1f170a6a6b1da46e67b0f8b266802ad9a2ec0`.

All indexed occurrences are included, reproducing H13's source population; the 242nd
resident occurrence must not be silently removed by applying a later clean-corpus
filter. The analyzer must emit a deterministic input manifest with every selected game,
raw-game hash, and trajectory hash. Missing inputs, duplicate game IDs, decode failures,
or turn-count mismatches are integrity failures.

Frozen reconstruction dependencies:

- `cgauto/fidelity_gap_audit.py` SHA-256
  `1ede4eef0b2f6af23c8b90b90603664b4701746483a73e764bb5b32d9d024a77`;
- `cgauto/analyze_d101a_production_suppression.py` SHA-256
  `9ffb10092180fa8a9ac848033650dc5d1c8fe95f83bff3a0aad9dc0dd37d4d30`;
- `cgauto/waste_sweep.py` SHA-256
  `cb5c813d591f3defd3809f97b25b61f6c7cdf67f039836d7b43c0544d29cad02`.

The resident source remains read-only at SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## 3. Frozen target event

For each cohort, decode the game from the named subject's seat. A target is one exact
crop generation satisfying all of:

1. the opponent successfully creates it with `PLANT`;
2. generation origin is exactly `opponent`, with a unique creator;
3. birth turn is strictly greater than 250;
4. the subject's bank-score margin in the state immediately before the PLANT is positive.

This is H13's literal event, upgraded from a successful-birth census to exact generation
lineage. Do not substitute command attempts, turn 250, post-turn margin, final outcome,
or an unrestricted opponent-origin generation.

## 4. Generation outcomes and access

Reconstruct both players' successful material actions against every target generation.
For each target report:

- game, subject seat, birth turn/cell/species, pre-turn margin, final margin, and turns
  remaining;
- Manhattan distance from the birth cell to the opponent shack;
- the subject's optimistic static-board BFS ETA at birth: the minimum over live subject
  units of `ceil(distance / movementSpeed)`;
- whether ETA is 0, at most 1, and at most the observed turns remaining;
- first subject and opponent contact turn and verb;
- subject/opponent HARVEST action count and fruit gained;
- subject/opponent CHOP action count and wood gained;
- generation death turn/feller or survival to the final decoded state;
- reconstruction quality and agreement between the two player-relative lineage passes.

Static BFS intentionally ignores future own-unit conflicts and decisions; because enemy
units do not block, it is an optimistic access diagnostic. Fruit/wood gained is carried
resource, not terminal score: fruit carried but not dropped scores zero. Report
`fruit + 4*wood` as **extracted score-equivalent**, never as banked points.

## 5. Primary replay-conditioned ceiling

For each target generation reachable within its observed remaining turns, define:

`observed_yield_swing_ceiling = 2 * opponent_extracted_score_equivalent`.

The factor two generously credits both denial of every observed opponent unit of yield
and capture/banking of the same value by the subject. It is a replay-conditioned ceiling
on the value visibly realized from these generations, not a theoretical upper bound on a
counterfactual policy. Sum it within game, assign zero to every cohort game without a
target or without opponent extracted yield, then average across all 242 resident games.

Also report:

- the ceiling conditional on a target game;
- a stricter missed-contact version restricted to generations the subject never contacts;
- raw opponent and subject extracted value without the factor two;
- target and positive-yield counts by game, seat, species, birth-turn band, and
  opponent-shack distance;
- the identical yamo measurements as descriptive fidelity context only.

The primary 95% percentile interval uses 20,000 deterministic whole-game bootstrap
replicates with seed `20260730`. Games, including their zero rows, are the resampling
unit. No event-level independence assumption is allowed.

## 6. Frozen verdict gates

Source/integrity support passes only if:

1. both exact cohort lists and every input/dependency hash match;
2. all 382 games decode with exact turn counts and no duplicate IDs;
3. every target has exact opponent origin, a unique successful PLANT event, and identical
   birth cell/turn/species in both player-relative lineage passes;
4. at least 30 resident target generations occur across at least 20 resident games.

Return `MATERIAL_CONTEST_OPPORTUNITY` only if support passes, at least 20 resident target
generations across at least 10 games have positive opponent extracted value, and the
resident all-game ceiling's bootstrap 95% lower bound is at least **20 margin**.

Return `NO_MATERIAL_CONTEST_OPPORTUNITY` only if support passes and that interval's upper
bound is below **20 margin**. Otherwise return `UNIDENTIFIABLE`, naming every failed or
boundary-crossing gate. No yamo comparison is a verdict gate.

## 7. Outputs and acceptance

Exclusive compact outputs:

- `cgauto/endgame_opponent_plant_contest.py`;
- `tests/test_endgame_opponent_plant_contest.py`;
- machine result and manifest under
  `local_codex_1/n5-endgame-opponent-plant-contest/`;
- canonical report/result under
  `data/analysis/live-agent-6553250/n5-endgame-opponent-plant-contest-*`.

Acceptance commands:

```text
python3 -m py_compile cgauto/endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py --self-test
python3 -m pytest -q tests/test_endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py <recorded exact arguments>
```

The full run must be deterministic apart from a non-hashed generation timestamp, reproduce
the frozen H13 target-event census, record all gates, and reproduce compact output hashes
on a second run. The reviewer checks event identity, score-versus-carry wording, the
generous factor-two ceiling, game-cluster uncertainty, and the causal boundary.
