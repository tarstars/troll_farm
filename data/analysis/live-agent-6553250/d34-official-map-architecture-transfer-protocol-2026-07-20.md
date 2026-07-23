# D34 official-map complete-architecture transfer census — protocol (2026-07-20)

## Purpose

D33 removed the largest known static simulator mismatch.  D34 now asks whether the project's
complete-policy conclusions survive on the exact official map distribution, and which controller
architecture is closest to the missing combination of resident suppression and renewable
production.

This is an architecture discriminator, not a parameter sweep.  The existing non-resident
controllers are frozen witnesses of distinct scheduling families.  A controller previously closed
on other evidence cannot become a candidate merely by ranking well here.  D34 does not authorize a
candidate, source integration, TestSession game, Arena submission, or resident replacement.

## Hypotheses

1. The exact official map distribution changes absolute outcomes and some architecture ordering,
   but does not erase the resident/productive-farm tradeoff.
2. Productive farm families will raise own score and renewable activity but allow materially more
   opponent compounding than the resident, especially against adaptive and worker-rich opponents.
3. Denial wrappers that operate on one worker or one crop timing rule will not preserve enough of
   the farm's production to cross the complete-policy gate.
4. If no frozen witness passes, the Pareto geometry will identify the next representation: a
   coherent joint scheduler that optimizes production and suppression together, rather than a
   worker transplant, phase handoff, pulse, or hand-written crop override.

## Frozen substrate

- Map generator: D33 `generate_official(seed: i64)`, accepted after 3/3 development and 120/120
  untouched archived-state parity.
- Referee: the existing exact Rust engine and corrected stall rule.
- Stable control: exact `SecureOrchardBot::new()` from `rust/src/bin/yamo_orchard_live.rs`.
- Every seed/candidate/opponent cell runs in both seats from turn one.  Controllers are newly
  instantiated for every game; there are no handoffs or shared mutable trajectories.
- Primary development seeds: signed decimal seeds **9,100,000 through 9,100,059** inclusive.
- Sealed confirmation seeds: **9,100,060 through 9,100,119**.  They remain unopened unless one
  frozen controller passes every development promotion gate.
- The seed is the primary statistical unit.  Seat and opponent cells are averaged inside seed
  before confidence calculations.

## Frozen architecture witnesses

| Label | Complete scheduling family | Prior status |
|---|---|---|
| `resident` | stable two-worker suppression plus secure orchard | control |
| `private2` | fixed two-worker productive farm | closed as a candidate; productivity witness |
| `ownership2` | ownership-aware productive farm | closed as a candidate; private-economy witness |
| `prefruit2` | productive farm plus first-fruit crop interruption | closed; coupled-denial witness |
| `gold_adaptive` | adaptive productive farm and workforce | opponent-compounding witness |
| `separated_denial` | adaptive farm with separately assigned denial capacity | closed; capacity witness |
| `hybrid3` | three-worker hybrid Gold scheduler | workforce witness |
| `accumulate4` | staged four-worker/two-chopper farm | scale witness |
| `norx3` | native three-worker imitation scheduler | closed; learned-structure witness |

These are intentionally broad architectural landmarks.  No constants are varied in D34.

## Frozen opponent panel

1. exact stable `resident`;
2. `gold_adaptive`;
3. `compact_gold`;
4. `norx_native_three`;
5. `legend_balanced`, the frozen worker-rich V2 mechanism proxy;
6. `mybot`;
7. `script_boss`; and
8. `silver_boss`.

The panel is a mechanism panel, not a calibrated Legend population.  Absolute mean margin cannot
be interpreted as Arena rating.  Cross-opponent robustness and paired changes from the resident
are the primary evidence.

## Execution matrix and telemetry

Development contains `60 seeds × 2 seats × 8 opponents × 9 controllers = 8,640` full games.
Before it, a two-seed integrity run must be byte-identical across two executions.

Each row records terminal turn, margin, both scores, all terminal inventories, terminal and maximum
worker counts, first third-worker turn, command counts by verb, successful planting attempts for
both sides, ambiguous simultaneous planting attempts, maximum/terminal plant count, and a
turn-ordered command hash.  Successful plant counts are attributed only when a commanded planting
cell was empty before the step and contains a new plant afterward; simultaneous claims are
reported separately.

## Frozen development analysis

For every controller, report:

- game-, seed-, seat-, and opponent-balanced terminal results;
- paired deltas from the resident in margin, own score, opponent score, wood, successful planting,
  maximum workers, catastrophe rate, and negative-margin mass;
- 95% normal intervals over 60 seed means;
- all eight opponent-family deltas and the worst family;
- the `gold_adaptive`, `norx_native_three`, and `legend_balanced` rich-opponent block separately;
- production/suppression Pareto membership using own-score delta (maximize) and opponent-score
  delta (minimize); and
- deterministic activation and integrity checks.

Catastrophe is frozen as terminal margin `<= -100`.  Negative-margin mass is the sum of
`max(-margin, 0)` over paired cells.

## Frozen promotion gate

A non-resident witness may open confirmation only if all conditions hold:

1. complete 960-cell grid and zero attribution/integrity failures;
2. seed-balanced mean margin delta from resident at least **+10**;
3. lower endpoint of its 95% seed interval is nonnegative;
4. own-score delta at least **+25**;
5. opponent-score delta at most **+5**;
6. at least six of eight opponent mean margin deltas are nonnegative and the worst is at least
   **-10**;
7. rich-block mean margin delta is nonnegative and rich-block opponent-score delta is at most
   **+10**;
8. catastrophe frequency does not increase; and
9. negative-margin mass is at most the resident's.

If more than one passes, select the highest seed-balanced margin delta; ties within one point go to
lower opponent score, then fewer workers, then fewer changed structural assumptions.

## Decision if no frozen witness passes

No holdout is opened.  D34 selects a **representation**, not a losing controller:

- if productive families add at least +25 own score but fail opponent suppression, while a denial
  witness reduces opponent score by at least 10 relative to its own productive parent but loses
  more than half of the parent's own-score gain, select a coherent joint production/suppression
  scheduler;
- if a denial witness preserves at least half of the productive parent's gain and reaches within
  five points of the opponent-score gate, select that whole-family grammar for a fresh optimizer;
- if no productive family adds +25 own score, return to first-move/recipe selection because the
  official maps invalidate the assumed production opportunity; or
- if the resident is Pareto-dominant, restrict the next cycle to resident-state residual value.

The selected representation must receive a new protocol and fresh data.  D34 results may not be
used to tune constants inside a closed witness.

## Planned artifacts

- runner: `rust/src/bin/d34_official_architecture_census.rs`;
- analyzer: `cgauto/analyze_d34_official_architecture_census.py`;
- focused tests: `tests/test_analyze_d34_official_architecture_census.py` and Rust unit tests;
- integrity TSVs, development TSV/JSON, and a written result in this directory.

