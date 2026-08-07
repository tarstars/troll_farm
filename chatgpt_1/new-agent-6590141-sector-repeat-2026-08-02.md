# Repeated sector analysis on the new E7a Arena agent

- Task: `20260802-new-agent-sector-6590141`
- Analyst: `chatgpt_1`
- Date: 2026-08-02 UTC
- Exact Arena identity: agent `6590141`, submission `41081503`, user `1302251`
- Source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- Source SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- Stable parent SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- Platform mutation: none

## Verdict

**`LIVE_RATING_TRANSFER_POSITIVE_BUT_TAIL_HEAVY; BEHAVIORAL_FAILURE_SECTORS_CONFIRMED; EXACT_FROZEN_MAP_SECTOR_SPLIT_PENDING_COMPACT_EXTRACTION`.**

The new agent reached a recorded mature score of **25.34 at rank 11/131**, the strongest mature
live score recorded by the project so far. That is encouraging transfer evidence for the complete
candidate. It is not causal evidence for the E7a rule: there is no same-window stable-parent A/A
control, the rule was selected on consumed development labels, and the later inventory snapshot
shows 25.26 rather than 25.34 while retaining rank 11.

The mature games reveal a much weaker terminal-margin distribution than the initial checkpoint.
The first 16 games were 11W/1T/4L, mean margin +41.69, with no catastrophes. The remaining 144
games were exactly 71W/2T/71L and contained all 35 catastrophic losses. Their losing games average
-139.01 margin. The initial sample therefore concealed rather than estimated the mature tail.

The repeated analysis also confirms three important behavioral sectors:

1. a liveness sector: 25/160 games contain a period-2 MOVE episode of at least six turns;
2. a non-renewable-production sector: only 10 of 1,704 attributed created crops were reaped;
3. an active endgame-conversion sector: 942 post-turn-250 planted crops were successfully chopped
   for wood.

The exact requested **frozen initial-map sector split** cannot yet be calculated from the committed
mature artifacts. The repository contains all 160 exact game IDs and a host-side decoded replay
run, but its per-game turn-1 rows have not been committed. I therefore do not infer the live
selected count from the development rate of 13/60, nor use chop outcomes as a proxy for the cached
focus choice. A fail-closed collector for the exact 160 games is committed and a host execution
request is remotely visible.

## 1. Evidence and identity

### 1.1 Exact initial checkpoint

The submission-scoped checkpoint at
`data/analysis/live-agent-6553250/e7a-sector-owner-override-initial-checkpoint-20260802T174600Z.json`
contains 17 exact battle rows: 16 finished and one pending. Every finished row parsed, identity is
clean, and there are no runtime markers or fetch failures.

Its 16 finished games are:

| Result | Count |
|---|---:|
| Wins | 11 |
| Ties | 1 |
| Losses | 4 |
| Mean margin | +41.6875 |
| Catastrophes (`margin <= -100`) | 0 |
| Negative-margin mass | 175 |
| Arena score/rank | 19.42 / 69 of 131 |

The four losses have total margin -175 and mean -43.75. The eleven wins have total margin +842 and
mean +76.55.

### 1.2 Exact mature identity

The public-battle inventory at
`data/analysis/live-agent-6553250/top15-public-battle-inventory-2026-08-02.json` lists exactly 160
finished games for agent `6590141`; all 160 rows carry submission `41081503`.

The mature agent report at `docs/reports/2026-08-02-e7a-sector-agent-description.md` gives:

| Result | Count/value |
|---|---:|
| Games | 160 |
| Wins | 82 |
| Ties | 3 |
| Losses | 75 |
| Mean margin | -29.3 (reported to one decimal) |
| Catastrophes | 35 |
| Catastrophe rate | 21.875% |
| Negative-margin mass | 10,045 |
| Mean loss margin | -133.93 |
| Recorded mature score/rank | 25.34 / 11 of 131 |

The later public inventory snapshot records score 25.26, still rank 11. The difference is a
snapshot fact, not a new code version: the exact agent and submission are unchanged.

## 2. Cold-start versus mature transfer

Subtracting the exact first 16 outcomes from the 160-game mature totals gives the 144 games added
after the initial checkpoint:

| Metric | Initial 16 | Added 144 | Mature 160 |
|---|---:|---:|---:|
| Wins | 11 | 71 | 82 |
| Ties | 1 | 2 | 3 |
| Losses | 4 | 71 | 75 |
| Win rate | 68.75% | 49.31% | 51.25% |
| Catastrophes | 0 | 35 | 35 |
| Catastrophe rate | 0% | 24.31% | 21.88% |
| Negative-margin mass | 175 | 9,870 | 10,045 |
| Mean loss margin | -43.75 | -139.01 | -133.93 |
| Mean margin | +41.69 | approximately -37.19 | -29.3 reported |

The added-144 mean margin is approximate because the mature report rounds its mean to one decimal.
All counts and negative-mass calculations are exact.

### Interpretation

The first checkpoint was not merely noisy in magnitude. It represented a different apparent
regime:

- its win rate was 19.44 percentage points higher than the following 144 games;
- it contained no catastrophe, while nearly one quarter of later games were catastrophic;
- the average later loss was 3.18 times as severe as an initial-checkpoint loss;
- after the first checkpoint, wins and losses were exactly balanced at 71 each, but the loss tail
  was extremely asymmetric.

This is a direct warning against assessing a newly submitted agent from 10-20 Arena games. It also
explains how a bot can achieve an attractive rating while having negative average terminal margin:
Arena score is not a direct transform of aggregate margin, and the opponent mixture matters.

## 3. Repeating the frozen E7a map-sector question

### 3.1 Frozen rule

For the resident seat, let:

```text
D_L = sum of BFS distances from own walkable shack doors to all initial LEMON trees
D_P = sum of BFS distances from own walkable shack doors to all initial PLUM trees
```

An unreachable tree contributes 10,000. The stable parent chooses LEMON on an exact tie and
otherwise chooses the smaller sum. The frozen E7a intervention applies only when:

```text
parent choice = LEMON
and
D_P - D_L <= 8
```

Inside that sector, the candidate caches PLUM; outside it, the candidate is behaviorally identical
to the parent focus choice.

No threshold, feature, or label is changed in this repeat.

### 3.2 What the committed mature evidence contains

The exact 160-game inventory contains game identity, participants, positions and submission IDs.
The mature report contains aggregate outcomes and behavior. The host top-15 audit decoded every
public replay and constructs an `opening` record per side, but its compact audit JSON and per-side
rows have not yet been committed. Therefore the current tracked evidence does not expose, for each
of the 160 games:

- `D_L` and `D_P`;
- the parent default species;
- whether the frozen near-tie sector fired;
- a stable map or initial-state fingerprint joined to outcome.

### 3.3 What I deliberately do not do

I do not:

- multiply 160 by the development support rate 13/60 and call the result live support;
- infer the cached species from which trees were eventually chopped;
- treat PLUM-focused and LEMON-focused games as randomized treatment arms;
- compare live score 25.34 to historical parent score 24.19 and call +1.15 the sector effect;
- use the later 25.26 snapshot as a separate replicate;
- reopen or rerun consumed E7 development maps.

### 3.4 Exact collector prepared

`chatgpt_1/new_agent_sector_6590141_collect.py` is a fail-closed public-replay collector for exactly
agent `6590141`, submission `41081503` and user `1302251`. It:

1. filters the battle list by exact agent/submission identity;
2. fetches only finished game results;
3. decodes frame 0 with the repository's checked-in parser;
4. computes `D_L`, `D_P` and the frozen sector from official turn-1 state;
5. stores only a compact row per game, with hashes rather than raw frames;
6. reports overall, selected, unselected, parent-PLUM and clear-LEMON strata;
7. bootstraps margins and reports same-opponent contrasts as descriptive only;
8. fails the whole extraction on any identity, fetch or parse error.

Collector commit:

```text
cdd28acb92ce372b139dbb490034aaf0584824d6
```

Host-run request:

```text
coordination/messages/chatgpt_1/
20260802T195500Z-20260802-new-agent-sector-6590141-host-run-request.md
```

Until its compact output is committed, the honest live map-sector result is:

```text
PENDING_EXACT_COMPACT_TURN1_EXTRACTION
```

## 4. Behavioral sector analysis from all 160 games

These sectors are directly supported by the mature public-replay audit and do not depend on the
missing `D_L`/`D_P` split.

### 4.1 Liveness sector

Twenty-five of 160 games, **15.625%**, contain a period-2 MOVE run of at least six turns. The most
severe documented case is game `897832286`: a worker carrying two WOOD alternates between two
cells for turns 160-286, a 127-turn episode.

This is inherited from the stable parent because E7a changes only the cached PLUM/LEMON focus
function. The failure can dominate any expected +4 development-margin signal. It is also a much
cleaner next engineering target than another strategic weight: the counterexamples are public,
the expected correct behavior is local, and a candidate can be required to preserve exact command
streams outside those counterexamples.

### 4.2 Renewable-production sector

Across the 160 games, the replay audit attributes 1,704 created crops to the agent, but only 10 are
reaped by the agent: **0.587%**.

This does not mean planting is globally useless, because most crops are intentionally conversion
assets. It does mean the live controller is not operating a broad harvest-replant economy. Any
future claim that the two-worker agent has become renewable must distinguish:

- protected orchard mothers;
- ordinary planted crops;
- post-turn-250 conversion crops;
- crops lost to the opponent;
- crops never reached before game end.

### 4.3 Endgame-conversion sector

The audit identifies **942 successfully completed post-turn-250 planted-and-chopped conversions**.
The conversion mechanism is therefore active at scale and is one of the parent controller's main
sources of terminal wood, not a rare fallback.

The useful next analysis is not “does conversion activate?” It is whether conversion value is lost
through target oscillation, failure to bank wood, or opponent capture, especially inside the 35
catastrophic games.

### 4.4 Workforce sector

The resident permanently caps itself at two workers. Several top agents reach worker three in more
than 80% of recent games and worker four in roughly 40-95%. The mature 35-catastrophe tail is
consistent with the previously documented scale-asymmetry problem, although this live deployment
alone does not identify a causal TRAIN intervention.

## 5. What the live result says about E7a

### Supported

- The complete E7a candidate is technically valid and competitive enough to reach rank 11.
- Its mature score exceeds the repeated stable-parent median of 24.19 and the parent's prior best
  recorded 24.77.
- The candidate did not introduce a new runtime or identity failure.
- The intervention is small enough that known live defects can be attributed to inherited parent
  behavior unless they depend on the changed focus species.

### Not supported

- A +1.15 causal rating gain versus the stable parent.
- Confirmation that the 13/60 development-sector support transfers to live Arena maps.
- Confirmation that live games inside the near-tie sector outperform the same games under parent
  control.
- Confirmation that E7a reduces catastrophic losses.
- Promotion of the consumed-panel +4.008 margin estimate to prospective evidence.

Even after the exact selected/unselected split is extracted, it remains observational because every
live game uses E7a. A causal field estimate still needs a contemporaneous parent control or an
appropriately frozen three-arm prospective protocol.

## 6. Ranked conclusions

### 1. Fix bank-bound period-2 movement before another strategic extension

**Status: strongest immediate engineering lead.**

The failure affects 25/160 games and includes a 127-turn cargo-carrying episode. A narrowly scoped
fix should be tested on all 25 public counterexamples, with exact control-stream preservation on
non-affected games and explicit proof that cargo reaches a bank rather than merely breaking the
ABAB signature.

### 2. Complete the exact live E7a sector split

**Status: measurement task, collector ready, compact host extraction required.**

The result will answer support and outcome-heterogeneity questions, but not the causal treatment
value. Required outputs are the selected count, selected/unselected margins and tails, seat split,
opponent-strength split, same-opponent descriptive contrasts, and map duplication audit.

### 3. Analyze catastrophic conversion and scale interactions

**Status: next replay analysis after liveness.**

The 35 catastrophes and 942 conversions are both large enough for a concrete mechanism census.
The useful discriminator is whether catastrophic games lose value through:

- unbanked carried wood;
- long movement oscillation;
- conversion crops taken by the opponent;
- too-late conversion cycles;
- opponent workforce expansion while the resident remains at two workers.

Do not create a bundle from these mechanisms before measuring them separately.

## 7. Current disposition

```text
Candidate live strength: encouraging, mature rank 11
Initial 16-game verdict: invalid as a transfer estimate
Mature tail: poor, 35/160 catastrophes
Frozen E7a live map-sector split: not yet available from committed rows
Causal E7a value: unresolved
Best next code change: narrow bank-bound liveness repair
```

No source, candidate, TestSession, Arena submission, sealed-data access or platform mutation was
performed in this repeat.
