# Conditional top-player opening archaeology — 2026-07-17

## Verdict

The replay corpus supports two non-control macro options for the next offline iteration:

1. **Farm-first orchard scale**, reconstructed primarily from `wala` (rank 2): buy a variable
   harvest/planting worker on turn 1, use two farming hands to create and harvest training-resource
   supply, add a wood/mining worker around turn 68, then conditionally add a second wood worker.
2. **Adaptive max-bank hybrid scale**, reconstructed primarily from `delineate` (rank 1): buy a
   strong hybrid whose stats are derived from the bank, remain compact on slow/remote openings,
   and add later hybrids only after the first pair has actively replenished the missing resources.

The exact promoted 62,725-byte policy remains the safe control.  This analysis does not justify
an arena write, a prospective holdout, or a live Monte Carlo controller yet.

The main strategic result is not “more workers are better.”  It is:

> Worker count is downstream of the opening's funding engine, renewable supply, role division,
> and target policy.  A third worker transplanted into the promoted trajectory is unaffordable or
> harmful, while a farming-first architecture deliberately creates the resources and jobs that
> make later workers productive.

## Scope and data quality

The analyzer joins official replay state reconstruction to exact player commands for every game
in the processed corpus containing a current top-20 agent or live agent `6553250`.

| Quantity | Result |
|---|---:|
| Unique games | 427 |
| Selected player occurrences | 618 |
| Replays whose decoded and command turn counts agree | 427 / 427 |
| Unknown replay-diff updates | 0 |
| Top-five occurrences | 129 |
| Live-agent occurrences | 161 |

Each occurrence now contains:

- seat-relative turn-one inventory, supply, reachability, water, iron, and shack geometry;
- opponent identity, first-five-turn commands, first train, and train count;
- every successful train's turn, requested and realized spec, exact cost, full deficit trajectory,
  affordability delay, funding window, and contributing worker actions;
- observed whole-bank score and wood recovery after each train, with horizon censoring recorded;
- every worker's actual/blocked moves, effective chops, harvested/planted/picked/mined material,
  drops, final cargo, productive and inactive turns, and direct deposit payback;
- per-agent train-count, train-sequence, planting-timeline, worker-role, funding, and conditional
  turn-one summaries.

The machine-readable source is
`top-player-opening-analysis-2026-07-17.json`.  It is observational replay archaeology, not a
causal policy comparison.

## Level 1 — population result

| Cohort | n | Mean successful trains | At least 2 trains | Median first train | Mean plants | Mean final wood |
|---|---:|---:|---:|---:|---:|---:|
| Current top five | 129 | 1.915 | 53.5% | 2 | 35.1 | 75.1 |
| Live `tass` | 161 | 1.000 | 0.0% | 8 | 10.7 | 48.2 |

The top-five train-count distribution is heterogeneous: 2 appearances with no train, 58 with one,
26 with two, 35 with three, and 8 with four.  `Escdemon`, ranked third in the snapshot, always
trains exactly once.  Therefore neither a fixed three-worker policy nor a fixed compact policy is
the population answer.

Per-agent outcomes are descriptive because opponents and game samples differ:

| Rank | Agent | n | Mean trains | First train | Mean plants | Final wood | Margin |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | delineate | 26 | 1.65 | 4 | 44.0 | 94.3 | +163.6 |
| 2 | wala | 29 | 2.62 | 1 | 55.9 | 102.7 | +136.2 |
| 3 | Escdemon | 26 | 1.00 | 11 | 6.6 | 36.0 | +25.4 |
| 4 | norxondor_gorgonax | 30 | 2.07 | 6 | 35.0 | 63.5 | +64.4 |
| 5 | laconic_pixel | 18 | 2.22 | 2 | 30.4 | 78.9 | +72.4 |
| 6 | tass | 161 | 1.00 | 8 | 10.7 | 48.2 | -25.8 |
| 7 | Konstant | 30 | 1.00 | 36.5 | 29.0 | 59.8 | +46.9 |
| 8 | Bubaptik | 80 | 2.00 | 12 | 26.7 | 58.8 | -63.7 |
| 9 | yaichi | 25 | 1.00 | 20 | 28.4 | 58.8 | +61.0 |
| 10 | viewlagoon | 26 | 3.62 | 1 | 59.1 | 80.4 | +88.0 |
| 11 | Astrobytes | 25 | 1.44 | 28 | 35.3 | 52.1 | +21.3 |
| 12 | putibuzu | 15 | 0.87 | 15 | 21.3 | 41.1 | +36.9 |
| 13 | yamo | 20 | 1.00 | 1 | 11.1 | 38.8 | -6.0 |
| 14 | MSz | 26 | 1.69 | 1 | 28.3 | 51.7 | +31.4 |
| 15 | Risen | 19 | 0.95 | 15.5 | 23.2 | 41.9 | +9.3 |
| 16 | Stounate | 19 | 0.95 | 2 | 28.8 | 46.7 | -11.2 |
| 17 | DoubtinGiyov | 17 | 1.12 | 1 | 21.6 | 33.9 | +12.1 |
| 18 | uta_ccc | 16 | 2.56 | 24 | 37.9 | 76.4 | +68.9 |
| 19 | gaha | 5 | 1.80 | 34 | 46.0 | 48.2 | +55.6 |
| 20 | xSkyline | 5 | 1.80 | 1 | 30.0 | 49.4 | -3.8 |

## Level 2 — coherent architecture families

The agents separate into four qualitative, per-agent families.  These are descriptions of
complete observed openings, not a pooled synthetic bot.

| Family | Agents | Opening worker | Later workers | Supply pattern |
|---|---|---|---|---|
| Compact wood-first | Escdemon, tass, Konstant, yaichi, yamo, Risen, Stounate | Usually harvest 0 / chop 2–3 | Normally none | Sparse to moderate; wood conversion starts early |
| Farm-first staged scale | wala, viewlagoon, MSz, uta_ccc, gaha, xSkyline | Harvest/generalist, chop 0–1 | Hybrid/wood workers | Build training-resource orchard, then add choppers |
| Hybrid adaptive | delineate, norxondor, Bubaptik, Astrobytes, putibuzu, DoubtinGiyov | Hybrid chopper | Conditional later hybrids | Mixed replenishment and wood throughout |
| Split/mixed | laconic_pixel | Wood specialist or generalist by game | Scales in half the sample | Modest early orchard, large late banana phase |

The compact family is a crucial counterexample to monotonic workforce scaling.  `Escdemon`
always has two total workers, plants only 6.6 trees per appearance, and still occupies rank 3.
Its games are shorter on average (218 turns), so its lower raw final wood is not directly
comparable to 300-turn `wala` games.

The live policy is already in the compact wood-first basin: its trained worker appears at median
turn 8, performs 33.7 effective chops per 100 active turns, and deposits 36.8 wood on average.
Merely copying `Escdemon`'s worker count would not create a distinct option.  The useful new
options are the two different funding/supply basins below.

## Level 3 — farm-first orchard scale (`wala`)

### Reconstructable turn-one rule

All 29/29 appearances train on turn 1.  The first worker's spec is reproduced exactly by:

```text
movement = min(2, floor(sqrt(initial PLUM  - 1)))
carry    = min(3, floor(sqrt(initial LEMON - 1)))
harvest  = min(2, floor(sqrt(initial APPLE - 1)))
chop     = 1
```

This is a farming hand, not the final chopper: 21/29 are classified harvest specialists, seven
generalists, and one carrier.

The second successful train occurs in 27/29 games from turn 39 through 100 (median 68):

- `2/2/0/2` in 17 games;
- `2/4/1/2` in 7;
- `1/2/0/2` in 2;
- `2/3/1/2` in 1.

The third occurs in 20/29 games from turn 81 through 177 (median 107.5): `2/2/0/2` in 14 and
`3/4/0/3` in 6.  All third trained workers are wood specialists.

### Supply is phased, not generic farming

Mean successful plantings per game:

| Turn window | PLUM | LEMON | APPLE | BANANA | Total |
|---|---:|---:|---:|---:|---:|
| 1–25 | 2.07 | 3.10 | 1.55 | 0.00 | 6.72 |
| 26–50 | 0.28 | 0.90 | 0.03 | 0.00 | 1.21 |
| 51–100 | 0.24 | 0.17 | 0.00 | 0.55 | 0.97 |
| 101–150 | 0.28 | 0.83 | 0.48 | 7.55 | 9.14 |
| 151+ | 2.24 | 5.72 | 1.28 | 28.59 | 37.83 |

The opening first creates PLUM/LEMON/APPLE supply needed to replenish the training bank.  The
large BANANA phase comes only after the workforce exists.  This is the opposite of transplanting
a worker into the current late, mostly banana-oriented supply loop.

### Funding division

The first train is entirely funded by the starting bank.  The second starts unfunded in all 27
games.  Its mean cost is `5.78 PLUM / 9.30 LEMON / 2.30 APPLE / 6.00 IRON`; both farming hands
harvest, plant, mine, and drop during the median-68-turn funding interval.

The third train exposes the role split most cleanly.  Its mean cost is
`8.50 PLUM / 10.60 LEMON / 3.00 APPLE / 8.50 IRON`.  During the funding window:

- starter drops on average `3.85 PLUM / 3.60 LEMON / 1.05 APPLE`;
- first trained farmer drops `4.40 PLUM / 6.20 LEMON / 1.65 APPLE`;
- second trained worker drops `8.65 IRON` and `2.80 WOOD`.

Thus the existing farmers almost exactly fund the fruit side while the first wood worker funds
the iron side.  The later worker is not bought by idle surplus; the preceding role system creates
its inputs.

### Lifetime roles and observed recovery

| Worker ordinal | n | Dominant role | Harvest / 100 active | Plant / 100 | Chop / 100 | Mean deposited wood | Direct-deposit payback |
|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 29 | Starter/farmer | 15.8 | 9.4 | 2.7 | 2.2 | n/a |
| 1 | 29 | Harvest specialist | 13.6 | 9.2 | 4.7 | 6.9 | 76 turns |
| 2 | 27 | Wood/hybrid | 0.4 | 0.0 | 34.4 | 58.4 | 47 turns |
| 3 | 20 | Wood specialist | 2.1 | 0.1 | 38.5 | 56.8 | 24.5 turns |

All workers are measured productive on 96–99% of their active turns; extra workers are not
merely standing around.  Direct-deposit payback ignores displaced work and iron cost and is only
a diagnostic.

Observed whole-bank recovery is slower for the foundational farmer and faster for later
choppers:

| Train | n | Median turn | Bank delta immediately | +25 turns | +50 turns | Median return to pre-train bank |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 29 | 1 | -12.86 | -15.07 | -7.28 | 68 |
| 2 | 27 | 68 | -17.07 | -2.15 | +16.63 | 26 |
| 3 | 20 | 107.5 | -21.45 | +33.30 | +102.00 | 12.5 |

These are observed bank trajectories, not no-train counterfactuals.  They nevertheless prove
that a four-turn or 25-turn rollout value would systematically reject the very investment that
creates this architecture.

### Conditional expansion signal

Twenty games reach the third train and nine do not.  The third-train games start with mean LEMON
7.25 versus 4.44, nearby fruit 6.9 versus 3.7, and nearest-tree distance 1.0 versus 2.2.  An
in-sample LEMON threshold of 6.5 has balanced accuracy 0.739; this is a discovery signal, not a
frozen selector.

No evidence here supports switching based on an opponent's first few commands.  Map supply and
starting-bank features are the stronger first selector candidates.

## Level 4 — adaptive max-bank hybrid scale (`delineate`)

All 26 games eventually train a first worker, at median turn 4.  Twenty-two are hybrid choppers.
In 22/26 games the chosen four stats are exactly the independently maximum affordable stats from
the bank immediately before training:

```text
stat(resource) = floor(sqrt(bank[resource] - current_worker_count))
```

The four exceptions reserve only one or two harvest levels; movement, carry, and chop still use
the maximum.  This gives a compact spec generator, although it does not by itself reconstruct the
task allocator.

Later expansion is conditional: 14 games stop after the first train, seven add a second, and five
add both a second and third.  The second train is at median turn 106 and is unfunded at the start
of every funding window.  The division of work is again explicit:

- starter drops 14.5 LEMON on average during the second-train window;
- first hybrid drops 7.5 IRON and 4.0 PLUM;
- mean second-train cost is 8.25 PLUM / 13.67 LEMON / 2.92 APPLE / 8.92 IRON.

The first hybrid remains genuinely mixed—6.5 harvests, 4.5 plants, and 28.7 effective chops per
100 active turns—while later workers become progressively more wood-heavy.  The second and third
trained workers deposit 65.3 and 83.6 wood on average.

The opening condition is materially associated with whether scaling continues:

- nearest tree distance is 0.5 in multi-train games versus 1.5 in one-train games;
- a descriptive `distance <= 0.5` split has in-sample balanced accuracy 0.762;
- the actual first-worker cost begins fully affordable in 14 games; 64.3% of these continue to a
  second train, versus 22.2% when the starting deficit is at least two resources;
- mean first-train turn is 11.1 in games that later scale versus 39.9 in games that remain small.

The zero-deficit versus two-plus-deficit comparison is a useful within-agent boundary, but it is
not randomized: map geometry, opponent interference, and the agent's own early actions all remain
confounders.

Mean planting is balanced across training and terminal resources: 10.65 PLUM, 10.23 LEMON,
2.08 APPLE, and 21.08 BANANA.  This option is therefore not “train max stats and fall back to the
current supply policy”; the mixed replenishment loop must be part of the implementation.

## Near-affordability and conditional evidence

Several within-agent comparisons point in the same direction:

| Agent | Low/high sample | Strongest descriptive condition | Low vs high observation |
|---|---:|---|---|
| delineate | 14 / 12 | Nearest tree at door | distance 1.5 vs 0.5 |
| wala, third train | 9 / 20 | Initial LEMON / nearby supply | LEMON 4.44 vs 7.25 |
| laconic_pixel | 9 / 9 | Shack separation | distance 5.33 vs 11.33 |
| viewlagoon | 6 / 20 | Nearby tree count | 4.83 vs 7.50 |
| Astrobytes | 14 / 11 | Initial PLUM | low-bank games train later |

Some signals are counterintuitive.  `norxondor` scales more often with lower initial IRON and
fruit, which likely reflects policy response, replenishment, opponent pressure, or sampling—not a
reason to prefer poor starts.  Thresholds are deliberately stored as in-sample descriptive
statistics.  They must not be copied into the live bot without paired option outcomes and blocked
validation.

Games in which variable agents scale also have much higher observed margins, but training count
is post-opening and affected by the same game trajectory.  This is evidence that the architectures
are coherent, not an estimate of the causal value of another worker.

## Candidate option specifications for Phase 2

### Option A — farm-first orchard scale

**Entry:** turn 1, only when the exact farmer spec above is legal and the shack can be cleared.
Initially run as a full option on discovery seeds, not behind a fitted map selector.

**Stages:**

1. Train the variable farmer on turn 1.
2. Assign starter and farmer to private/defensible PLUM, LEMON, and APPLE harvesting and planting.
3. Target a `2/2/0/2` wood/mining worker; rich-LEMON upgrades are a later ablation, not part of the
   first implementation.
4. Target a second `2/2/0/2` only after the two farmers can cover fruit cost and the first chopper
   can cover iron cost without abandoning an immediately bankable fell.
5. Transition to banana/wood cashout only after the training-resource orchard and roles are live.

**Abort:** if the first wood worker is not affordable by turn 100, if defensible training-resource
supply collapses, or if the option loses exclusive access to its planting cells, stop further
training and hand the existing units to the promoted controller.  Third-worker timeout and supply
thresholds remain telemetry in discovery; do not fit them yet.

**Required telemetry:** stage, target cost and deficit, private planted supply by kind, worker
funding contributions, displaced baseline tasks, train success, bank recovery, wood captured by
each side, and handoff reason.

### Option B — adaptive max-bank hybrid scale

**Entry:** use the maximum-affordable spec generator, with harvest optionally capped one level
below maximum, only when the first target is already affordable or a door-adjacent tree gives a
short explicit funding path.  Poor starts remain on the exact control.

**Stages:**

1. Buy one max-bank hybrid and assign it a mixed chop/harvest/plant role.
2. Replenish all four training resources with the starter biased toward LEMON and the hybrid
   biased toward IRON plus PLUM, matching the observed funding division.
3. Permit one later max-bank hybrid only after the funding bank is earned by post-entry work and a
   useful private wood target exists.
4. Permit another expansion only as a separate activation ablation; the first Phase-2 build caps
   at three total workers.

**Abort:** no initially unfunded entry without a short measured path; no second train after turn
125; no train that consumes a resource required for an immediate baseline cashout; and immediate
handoff if the selected private supply becomes opponent-favored.

**Required telemetry:** all Option-A fields plus max-affordable stat slack, nearest-tree condition,
time-to-first-train, and the exact resource that prevents continuation.

These are complete opening hypotheses.  They are not “add one worker” switches, and they must be
implemented outside the live submission before any byte-budget work.

## Implications for the controller and Monte Carlo program

1. The first search action is an option choice: exact control, farm-first scale, or adaptive
   hybrid scale.  Primitive random command mutation remains closed.
2. Turn-one map/bank features currently carry more evidence than opponent-opening features.  Fit
   a turn-one selector first; earn any turn-2–4 switch with measured incremental value.
3. The farm-first option requires at least a roughly 70-turn or terminal continuation.  Short
   asset bonuses will undervalue it.
4. Later expansion decisions are natural residual checkpoints.  Search at the second/third-train
   boundary, not on every movement turn.
5. Compare each option to exact control from the same root with common opponent/movement samples.
   The useful quantity is paired option delta after full funding and handoff.
6. Whole-bank recovery and direct worker deposits are mechanism diagnostics only.  Phase 2 must
   measure the counterfactual margin, displaced work, opponent capture, and tail risk.

## Phase-1 exit decision

Phase 1 passes its evidence gate:

- two distinct macro architectures have explicit entry, spec, funding, supply, role, abort, and
  handoff hypotheses;
- the farm-first turn-one spec is reproduced exactly in 29/29 games;
- the adaptive first spec is reproduced by a max-bank rule in 22/26 games;
- role-level funding and lifetime work are measured, rather than inferred from final worker count;
- short-horizon payback bias and causal limits are explicit.

Proceed to **Phase 2 on reused discovery seeds only**.  The first implementation order is Option A
with a fixed `2/2/0/2` later worker, then Option B capped at three total workers.  Freeze no
selector threshold, consume no prospective block, and make no arena change during this phase.

## Reproduction

```bash
uv run --no-sync python cgauto/top_player_opening_analysis.py --jobs 16
uv run --no-sync pytest -q \
  tests/test_top_player_opening_analysis.py \
  tests/test_top_player_macro_census.py \
  tests/test_replay_state.py
```

The full 427-game analysis takes about three seconds with 16 processes on this machine.  The
focused validation currently passes 13 tests.
