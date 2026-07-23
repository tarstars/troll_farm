# Robust first-option discovery — 2026-07-18

## Verdict

**Close the isolated first-worker option search.**  A complete 29-option library, eight
heterogeneous continuation models, an identical-run audit, and six independent process-level
replications found no opponent-robust activation.  Exact-resident abstention is therefore the
only qualified decision.

The untouched map holdout was not opened.  No candidate was packaged, no live artifact or submit
default was changed, and no arena write was made.

## What was tested

The research-only Yamo copy can force a legal harvest-0 first worker and then use the exact
resident continuation.  The option grid contains:

- exact resident control;
- the dynamic maximum-affordable harvest-0 worker;
- all 27 fixed `movement 1..3 / carry 1..3 / harvest 0 / chop 1..3` workers.

Unaffordable fixed workers are exact control.  Every affordable option was evaluated from both
seats to terminal or exact stall against GoldElite, SchedBot, MyBot, SilverBoss, BossReal,
ScriptBoss, PrinterBot, and adaptive GoldElite.  Sixteen to twenty worker threads were used; the
workload is terminal simulation, not serial Python orchestration.

The initial discovery grid covers 60 consumed seeds, 120 seat cells, 29 options, and eight
models: 27,840 terminal comparison rows.  The first strict expanded rule required every visible
model delta to be positive and otherwise used exact resident.

## Level 1 — single-grid selector result

The expanded strict selector selected zero cells.  Allowing one nonpositive model with a `-10`
floor also selected zero.  Allowing two nonpositive models with a `-30` floor selected one cell,
but leave-one-model-out evaluation had eight held loss seeds, worst held-model mean `-1.267`, and
worst held seed `-52.5`.

The older four-model strict rule selected one discovery cell.  Its leave-one-model-out result was
also negative: worst held-model mean `-2.075`, 12 held loss seeds, and worst held seed `-52.5`.
This already failed the frozen discovery gate.

## Level 2 — identical-run stability

A fresh process repeated seeds 0--19, producing 9,280 rows on exactly the same map, seat, model,
and option keys.

- Opening activation and first TRAIN command: **9,280 / 9,280 exact**.
- Complete terminal tuple: 7,109 / 9,280 exact (76.61%).
- Option delta changed in 502 rows; its positive/zero/negative class changed in 52, including 46
  strict positive-to-negative or negative-to-positive flips.
- BossReal, GoldElite, and SchedBot were exact in 1,160 / 1,160 rows each.
- Adaptive Gold was 1,156 / 1,160; SilverBoss 1,122 / 1,160; ScriptBoss 775 / 1,160;
  PrinterBot 395 / 1,160; MyBot 181 / 1,160.

The option library is deterministic; several continuation policies are not.  Their source uses
process-randomized hash collections in decision paths, consistent with the observed fresh-process
variation.  Those outcomes are legitimate stochastic scenarios, but one process is not a
deterministic label and independent control/option instances are not a common-randomness pair.

The strict expanded selector remained inert in both runs.  The strict original-four decision
changed on seed 12, seat 1: the first run abstained and the repeat selected `m2c2k1`.

## Level 3 — replicated Monte Carlo result

Four more fresh processes completed the same 20-seed grid, giving six independent realizations,
40 seat cells, and 55,680 terminal comparison rows.  Three predeclared opponent-robust rules were
tested:

| Rule | Full-grid selections | Leave-one-repetition-out selections |
|---|---:|---:|
| every observed model/replicate delta positive | 0 | 0 |
| every model's replicate mean positive | 0 | 0 |
| every model's one-sided 90% lower bound positive | 0 | 0 |

A deliberately non-robust pooling diagnostic selected two cells.  It is a useful negative
control:

- seed 2, seat 1 selected max-bank because adaptive Gold predicted `+244`, despite means of
  `-22` BossReal, `-16` PrinterBot, `-13` SchedBot, and `-20.5` ScriptBoss;
- seed 15, seat 1 selected `m2c1k2`, despite deterministic `-28` GoldElite and `-1`
  SilverBoss plus mean `-8` MyBot.

Across six leave-one-repetition-out folds, that pooled rule made 13 selections but produced 48
held model-seed losses, worst held-model mean `-0.392`, and worst held seed `-16`.  Pooling a large
gain from one continuation over several opponent-specific losses recreates the exact failure mode
seen in the arena.  It cannot rescue the robust gate.

## Level 4 — controller conclusion

The plateau is not caused by an incomplete enumeration of first-worker stats.  The complete
harvest-0 grid contains no option that is even positive in mean under every continuation on this
discovery slice.  More samples could estimate the same negative cells more precisely, but cannot
turn the deterministic `-22`, `-28`, or `-13` disagreements into uncertainty.

The tested action is also narrower than the worker-rich architectures used by strong bots: it
changes one TRAIN and hands the worker to the resident continuation.  It does not co-design the
renewable supply loop, role allocation, later training, and target policy that make a larger
workforce productive.  The earlier full farm-first reconstruction tested that coupled direction
and lost heavily, so reopening it requires a materially better learned continuation, not another
funding constant.

## Decision and next protocol

Phase 7 fails and is closed:

1. retain resident agent `6559583` and the exact 62,725-byte source;
2. do not freeze or validate any first-worker selector from this consumed discovery set;
3. keep the untouched map block sealed;
4. do not package, time-gate, or submit an inert controller;
5. use the known 60 arena replays only to calibrate continuation-model relevance.

The next bounded iteration is **opponent-model calibration**, not a larger blind option grid.
Score each local continuation's action agreement on actual arena opponent trajectories, construct
an uncertainty set over behaviorally supported models, and evaluate decisions with both
process-level replication and held-model stress.  If calibrated distributionally robust selection
is still inert, retire first-move Monte Carlo and move to learned complete-policy continuations.

## Reproducible evidence

- `robust-first-option-discovery-0-59.tsv`
- `robust-first-option-discovery-2026-07-18.json`
- `robust-first-option-repeat-audit-2026-07-18.json`
- `replicated-first-option-study-2026-07-18.json`
- `cgauto/robust_first_option_study.py`
- `cgauto/robust_option_repeat_audit.py`
- `cgauto/replicated_first_option_study.py`
- `rust/src/bin/yamo_option_rollout_time.rs`

Final validation: 318 Python tests pass, the full release Rust suite passes, the Rust option
grid's three inventory/affordability/activation tests pass, formatting is clean, and
`git diff --check` is clean.  Only the repository's pre-existing warnings and ignored tests
remain.
