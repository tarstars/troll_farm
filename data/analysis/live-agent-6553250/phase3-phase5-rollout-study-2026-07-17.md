# Phase 3--5 option-selection and live-rollout study — 2026-07-17

## Verdict

The first complete option-level Monte Carlo candidate passes its frozen local protocol and its
deployment gates.  The selected architecture is a **turn-one, two-rollout controller**:

1. roll promoted pre-seed/coverage Yamo to the terminal/stall horizon against CompactGold;
2. roll the immediate maximum-affordable movement/carry/chop, harvest-0 worker option followed
   by the same promoted Yamo policy against the same continuation;
3. select the option only when its terminal margin exceeds control by more than 30 points;
4. otherwise, or on worker failure/deadline, use the exact promoted policy.

The standalone candidate is
`cgauto/submissions/candidate-agent6553250-compact-gold-rollout30.min.rs`: **90,643 bytes**,
SHA-256 `f5df1f760791a21ad0193469c132fea02ebaa2856b33f62213765205b3b59370`.
It has not been submitted.  The local pass permits a separately authorized controlled arena
trial; it is not an arena-performance claim.

## What was tested

The policy library was deliberately small.  The control is the exact promoted 62,725-byte
policy.  The only non-control option changes the first trained worker to the immediate
maximum-affordable movement/carry/chop specification with harvest zero, then hands control back
to normal stateful Yamo.  Applied globally, this option loses badly; the question is whether a
controller can isolate the rare maps where it helps.

All policy outcomes use exact Python-generated maps, the corrected referee engine and stall
condition, both seats, and the fixed deterministic opponent set `chopharvest`, `race`,
`ringfix3`, `taskplan`, and `yield`.  Local play is a paired self-harm/mechanism filter, not an
arena predictor.

## Phase 3 — option league and static selection

The full global option has real selectable upside but is unsafe without a guard.  On independent
seeds 120--179 it averages **-9.57** score margin if used everywhere, with 23 positive, 31 tied,
and 66 negative seat cells.  The seat-wise hindsight oracle remains positive at +5.395
seed-balanced margin, so the plateau is a selection problem rather than the absence of a useful
counterfactual.

Four exact local opponent continuations were evaluated first: GoldElite, SchedBot, MyBot, and
SilverBoss.  Their ensemble mean had useful but insufficient transfer.  Across reused seeds
0--119 its predicted/actual Pearson correlation was 0.423 and sign agreement was 81.7%.  A
positive-ensemble selector gained +2.893 but retained 15 losing seeds.  Requiring unanimous
positive signs selected only one of 240 seat cells and still had a slightly negative worst
opponent mean.  The larger ensemble was therefore neither robust enough nor byte-feasible.

The strongest single continuation was GoldElite with a conservative margin.  On discovery
seeds 0--59, `Gold delta > 30` was the smallest coarse threshold among 0/5/10/20/30 that had no
losing selected seed and positive means against every opponent.  It selected five seat cells and
scored +3.797 seed-balanced margin, 5 wins / 55 ties / 0 losses, minimum 0.  Without changing the
rule, seeds 60--119 selected four cells across three seeds and scored +3.612, 2/57/1, minimum
-4.8; every opponent mean remained positive.

## Phase 4 — frozen direct rollout validation

The rule, option, continuation, threshold, five opponents, seeds, and pass criteria were frozen
before opening seeds 120--179.  The predeclared gate required positive mean, every opponent mean
nonnegative, minimum seed delta at least -10, no more than two losing seeds, and exact fallback.

The frozen rule passed:

| Measure | Independent result |
|---|---:|
| Selected seat cells / seeds | 4 / 4 |
| Seed-balanced mean delta | **+2.717** |
| Seed W/T/L | 3 / 56 / 1 |
| Minimum seed delta | -2.6 |
| Worst-decile mean | -0.433 |
| Worst opponent mean | **+1.375** |

Opponent means were +2.650 `chopharvest`, +3.333 `race`, +1.375 `ringfix3`, +3.608
`taskplan`, and +2.617 `yield`.  The four selections were seed/seat `(120,1)`, `(143,1)`,
`(163,0)`, and `(179,0)`.  The normal-approximation interval still crosses zero because the
mechanism is sparse; the result passes the predeclared sparse gate but does not establish a
high-precision population effect.

CompactGold is a fixed deployment form of `GoldElite::new()`.  Removing environment knobs,
alternate constructors, and write-only state preserved 40/40 dynamic command streams and
240/240 terminal rollout cells exactly.

## Distillation result

A static tree was trained only after the direct rule was frozen.  Training used 1,880 seat cells
from seeds 0--119 and 180--999, with seeds 120--179 excluded from fitting and model selection.
Only 128 training cells were positive.  Blocked cross-validation selected a depth-5,
minimum-leaf-8, negative-weight-2 tree, but it found only 3/128 positives with 9 false positives.
The final fit had 0.80 precision and 0.0625 recall.

On the excluded block it found **0/4** direct-rollout activations and added two false positives.
Those false positives produced +0.173 mean overall but a -0.225 worst-opponent mean, while the
four missed direct decisions were worth +2.717.  Static feature distillation is closed for this
option: the boundary depends on long interaction, not a stable shallow partition of turn-one
features.

## Phase 5 — standalone deployment gates

The source budget is:

| Component | Bytes |
|---|---:|
| Selectable slim promoted parent | 63,305 |
| Exact engine | 14,101 |
| Exact rollout state | 847 |
| CompactGold | 9,256 |
| Conversion, controller, and module glue | 3,134 |
| **Total** | **90,643** |

The two terminal games run in scoped worker threads only on the first turn.  A shared 700 ms
deadline returns control if either game is unfinished; thread failure also returns control.  The
real bot then keeps one freshly constructed selected policy for the entire game.  Later turns do
not run the engine or selector.

The reproducible release gate recorded:

- 120/120 frozen first-turn decisions equal the precomputed CompactGold labels;
- exactly the four intended cells select the option;
- 10/10 complete dynamic command streams and terminal states equal the corresponding global
  option or promoted-control binary, including all four activations;
- standalone `rustc --edition 2021 -O -D warnings` compilation succeeds;
- first-turn wall time over 120 processes: mean 147.41 ms, p50 144.03 ms, p95 184.07 ms,
  maximum 193.96 ms, against the official 1,000 ms limit;
- five direct CPU samples used 115--135%, confirming that the two expensive games execute
  concurrently rather than as one serial Python workload.
- the complete repository regression closed with 300/300 Python tests passing and the full
  release Rust suite passing (existing ignored tests and unrelated warnings unchanged).

The exact machine-readable gate is
`data/analysis/live-agent-6553250/compact-gold-rollout-live-gate-2026-07-17.json`.

## Decision and limits

Promote this source to **locally qualified arena candidate**, not to live resident.  Further
static tuning on the consumed blocks is more likely to overfit than help.  The next informative
step is a controlled platform bracket with a healthy same-code capacity control, followed by the
candidate only under explicit arena authorization.  Keep the 62,725-byte resident and
`cgauto/api_submit.py` unchanged until then.

Important limitations remain:

- the independent block has only four activations and its interval crosses zero;
- CompactGold is one deterministic opponent continuation, not a model of the arena field;
- the local engine and command parity are exact for tested streams, but platform CPU contention
  and arena transfer require direct measurement;
- the live option is intentionally narrow; it does not solve worker-rich macro architecture in
  general and it does not justify later-turn Monte Carlo under the 50 ms budget.

## Reproducible artifacts

- `data/analysis/live-agent-6553250/compact-gold-rollout-gate-protocol-2026-07-17.md`
- `data/analysis/live-agent-6553250/compact-gold-rollout-validation-120-179.json`
- `data/analysis/live-agent-6553250/compact-gold-rollout-distillation-2026-07-17.json`
- `data/analysis/live-agent-6553250/compact-gold-rollout-live-gate-2026-07-17.json`
- `cgauto/local_model_rollout_transfer.py`
- `cgauto/rollout_selector_distillation.py`
- `cgauto/make_rollout_live_candidate.py`
- `cgauto/validate_rollout_live_candidate.py`
- `rust/src/strategies/compact_gold.rs`
