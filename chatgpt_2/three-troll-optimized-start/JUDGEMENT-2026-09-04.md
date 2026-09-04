# How I would improve the three-troll bot

**Agent:** `chatgpt_2`  
**Date:** 2026-09-04  
**Task:** `20260903-three-troll-optimized-start` judgement round  
**Scope:** diagnosis and ranked proposals only; no bot, panel, ladder, platform or Arena action

## Verdict in one paragraph

I would **not patch the submitted bot in place**. Its first defect is architectural: before the third-troll optimizer even gets a vote, the shared Stage-2A opening irreversibly buys a harvest-capable, chop-1 second troll and then hands that altered state to a champion continuation designed around a different roster. All five candidate “stall” maps are also control “stall” maps and have the same recorded play at the level exposed by the smoke result. The third-troll search therefore did not cause those five. It actually removes four of the control's nine inactivity flags by continuing to issue funding work, but that extra activity is not value: on the fourteen maps where it trains a third troll it scores 198 points less than its own control, 14.1 points per map, and loses on twelve of fourteen map comparisons. The right successor is a fail-closed final-value planner with the unchanged champion as its true incumbent, `PLANT` and `TRAIN` in one finite-forest action space, and `NO_TRAIN` as the default until the third troll beats the same optimized orchard without that troll.

## Evidence read

Primary artifacts:

- `chatgpt_2/three-troll-optimized-start/results/smoke.log`
- `chatgpt_2/three-troll-optimized-start/results/control-smoke.log`
- `chatgpt_2/three-troll-optimized-start/results/summary.json`
- `chatgpt_2/three-troll-optimized-start/make_candidate.py`
- `chatgpt_2/three-troll-optimized-start/optimizer.rs.in`
- `claude_1/opening-solver/stage2a/dispatcher.rs.in`
- `local_claude_1/third-troll/smoke.py`
- `chatgpt_1/start-game-optimizer/DESIGN-2026-09-04.md`
- ladder package `local_claude_1/ladder-queue/games-41239996/`

The submitted bot read **14.07** against the champion's **18.72** and scored about **21.9 fewer own points per game** by the package means, despite meeting a weaker field. That is the deficit to explain; training a troll early is not itself a success criterion.

## What “stalled” means here

The smoke harness does not report a process crash or the referee's end-of-game `has_stalled` result. Both arms:

- answered all 300 turns;
- produced no referee errors;
- produced clean telemetry.

The harness calls a map stalled when one of our trolls has a longest run with no active command at least **20 turns longer** than the resident's longest run over the same window. If there is no third troll, it calls turns after the second `TRAIN` through turn 200 the “funding window” even for the control whose optimizer is disabled, then separately checks turns 201–280.

This is a useful fail-closed mechanics alarm, but it is not the same as “lost the game”. Two of the candidate's five flagged maps outscore the resident in the smoke result:

- `daadbfd7e8423f86`: 136 against 100;
- `2d8f315778eba2a8`: 136 against 124.

Three of the control's nine flagged maps also outscore the resident. So the inactivity must be fixed before value is trusted, but the word `stall` must not be used as a direct score label.

## Why the candidate flags five maps and the control flags nine

### 1. The five candidate flags are inherited from the shared base

Candidate flags:

```text
64b1d4b14f026f9f
a6062948c27575a8
daadbfd7e8423f86
2d8f315778eba2a8
879f73412b531333
```

Every one is also a control flag. On every one:

- the same second troll is bought at the same turn;
- no third troll is trained;
- the final own score is the same in candidate and control;
- the plant count/timeline summary is the same;
- the idle maxima are the same.

The code explains the identity. The control sets `OPENING_ENABLE_THIRD = false` and hands back as soon as two trolls stand. The candidate also permanently hands back on the first two-troll state for which no third plan is admitted. On these five maps the candidate's third-troll machinery therefore never changes play.

**Conclusion:** the common five are not a third-troll-search bug. They come from the irreversible opening state shared by both arms.

### 2. The shared opening buys the wrong kind of second troll for the continuation

The Stage-2A second-troll rule is capped at `2/2/2/1`; its ordinary delayed target is `2/2/1/1`. Thus it deliberately buys a second **harvester/generalist with chop power 1**. All nine flagged control rows have harvest power 1 or 2 and chop power 1.

The resident champion usually reaches its continuation with a different division of labour: the original troll can harvest, while the second troll is commonly a harvest-0 lumberjack with chop 2 or 3. The control changes that roster and then immediately asks the unchanged champion to operate it. Nothing in the control proves that the champion's later candidate ranking, regeneration commitments and endgame feasibility rules remain productive under that new roster.

The result is long task-starvation windows. Examples from the control artifact:

- `64b1...`: both trolls have no active command for all 80 checked turns from 201–280; the second is `2/2/2/1`.
- `a606...`: the longest opening-window inactivity is 86 turns; the second is `2/2/2/1` and the planting log has a large gap after turn 110.
- `b64b...`: the second is `2/2/2/1`, no planting happens until turn 252, and the arm finishes 69 points below the resident on that map.
- `879f...`: both checked post-horizon streaks are 80 turns with a `2/2/1/1` second troll.

The artifacts do not log the champion's rejected candidate reason on each idle turn, so I cannot honestly distinguish, map by map, among “no tree”, “hands full”, “too slow to fell and bank before the horizon”, and “role/candidate ranking produced no task”. The direct diagnosis supported by the evidence is narrower and sufficient:

> an irreversible generalist second-troll purchase is handed to an unvalidated continuation, with no progress invariant and no way to restore the champion's original roster.

The exact per-turn rejection reason should be added to telemetry before anyone claims a more specific cause.

### 3. Why the candidate has four fewer flags

The control-only flags are:

```text
c84154d29ea19fbc
2433a442a41ce6cb
21d2746745cd7896
b64b9915e3f228af
```

On three of these the candidate trains a third troll; on `21d...` it enters the funding pathway and later hands back without completing the train. Those extra assignments keep trolls receiving commands, so the relative-idle alarm no longer fires.

But the four-map score difference candidate minus control is only **+1 point in total**:

```text
c841...  -16
2433...  -12
21d...    +24
b64b...    +5
sum         +1
```

So the reduction from nine inactivity flags to five is not evidence that the third-troll policy is good. It is evidence that the optimizer can generate work. Work and value are different.

## What the third-troll decision did to value

The 24-map development smoke gives a clean descriptive decomposition, though not a holdout verdict:

- candidate versus resident: **-416**, or -17.3 points per map;
- control versus resident: **-242**, or -10.1 points per map;
- candidate versus control: **-174**, or -7.25 points per map.

On the fourteen maps where the candidate actually trains a third troll, map-level candidate-minus-control differences sum to **-198**, or **-14.1 points per trained map**. Twelve of fourteen are negative; the two positives are +3 and +5. On the ten maps without a completed third troll, candidate versus resident sums to +50.

This is stronger than saying the net-value threshold was miscalibrated. The admission objective had the wrong target. It estimated a third troll's continuation value from a fixed visible forest and a local wood-rate surrogate. It did not evaluate the final paired game under the same optimized planting world with and without that troll. Therefore it systematically rewarded an early cheap roster that could not repay its irreversible cost.

## Ranked improvements

The estimates below are decision ranges, not promises. Rating is nonlinear and the identical champion file now spans about 2.2 ladder points, so no sub-2.2 ladder estimate should be treated as measurable.

### 1. Make the unchanged champion the real, byte-identical incumbent

**Change.** Delete the special early-second-troll pathway as a mandatory prelude. The optimizer may propose a second troll, but the live bot follows a continuously advanced shadow champion until one complete replay-valid plan beats that champion. `NO_TRAIN` and immediate champion continuation must always be legal. An optimizer-off build must be byte-identical to the champion, not merely “the same opening with one constant changed”.

The important consequence is reversibility: before an irreversible `TRAIN`, the plan must already include the roster, planting, work allocation and hand-back state that justify it. After a failed search, nothing has been spent and the champion simply continues.

**Expected size.** Relative to the submitted bot, this should recover roughly **15–22 own points per game** and about **3–5 rating points**, because that is the observed distance back to the champion. This is recovery to baseline, not an expected gain above it. Relative to the invalid no-optimizer control, the development smoke suggests about **10 points per game** of recovery by removing the shared opening regression.

**Falsification.** This proposal is wrong if any of these occurs:

- optimizer-off command streams differ from the frozen champion on any fresh mechanics case;
- either arm fails 100% mechanics on a fresh, unrevealed set;
- the shadow champion's state at hand-back does not reproduce a continuously running champion;
- admitted plans do not have positive paired final margin with a lower confidence bound above zero on the sealed holdout.

This is the first change because without it every later comparison can again be between two damaged arms.

### 2. Search planting and training in one finite-forest, final-value problem

**Change.** Use the event-driven DP/oracle architecture now being built by `chatgpt_1`, with one mutable future-forest state shared by forecast, admission and emitted commands. Optimize paired final score margin under exact continuation, not troll arrival or local resource rate. Keep every species on the frontier:

- banana: mature health 6, four wood, no training-resource cost;
- plum/lemon: health 12, four wood, also training resources;
- apple: health 20, four wood, fastest water-side growth but expensive to fell.

Water-adjacent cells are scarce, and tree count and distance are one decision: the median map has about 11.5 free cells within two steps and 27 within four, with only 2 and 5 water-adjacent. The search must charge seed, pick, travel, plant, growth, raid risk, chop, carry and bank time. A rate-times-remaining-turns estimate may be only a labour bound, capped by explicit surviving tree mass.

**Expected size.** If the orchard hypothesis is real, my prior is **+8 to +20 final own points per game above the unchanged champion**, with a possible **+2 to +4 ladder points**. The lower end is more credible than multiplying 16 gross points by every planted tree: most of the 16 is consumed by planting, travel, raid, felling and carry constraints. This is the only proposal here with a plausible above-champion effect larger than the ladder noise floor.

**Falsification.** Stop the line if:

- the offline `PLANT`-aware best is below +8 paired final-margin points on development data or selects the no-plant champion almost always;
- predicted added wood has mean absolute error above two wood or 90th-percentile overstatement above 1.5 times realised wood;
- the sealed holdout's paired-margin lower bound is not above zero;
- own-score lower bound is negative;
- the effect reverses under the high-raid scenario or either arm fails mechanics.

### 3. Treat the third troll as a marginal choice inside that orchard, with `NO_TRAIN` as the default

**Change.** Compare two separately optimized worlds from the same state:

```text
best final value with PLANT and TRAIN available
minus
best final value with the same PLANT action space but the third TRAIN disabled
```

Do not compare “third-troll bot” with a control that also changes the second troll. Do not require a third troll at all. A two-troll banana wood orchard is a valid result. If a third is selected, its talents must be chosen from the full legal frontier and its extra tree-conversion capacity must be backed by explicit surviving wood.

**Expected size.** Simply suppressing the current third decisions is worth about **7–8 own points per game relative to the submitted bot** on the development smoke; on the subset where the third was trained, the recovery is **14.1 points per map**. That is recovery, not evidence that a new third troll can beat the champion. A genuinely positive third-troll contribution is currently **unknown** and should be budgeted as 0 until the marginal world comparison proves otherwise.

**Falsification.** The default-no-train judgement is wrong only if, on a sealed holdout:

- the subset of states where the optimizer selects `TRAIN` has paired final-margin lower bound above zero;
- paired own-score is non-negative;
- forecast calibration passes;
- the result is non-negative in at least three opponent archetypes, including high raid.

If those conditions do not hold, remove the third-troll branch rather than retune its minimum-net constant or deadline.

### 4. Keep the joint assignment machinery, but put a progress certificate around execution and hand-back

**Change.** Preserve the joint command selection and live re-rooting, but make every active macro carry a measurable next event: inventory change, crop release, tree-health reduction, bank, train, or bounded movement toward a reserved target. If that event does not occur by its certified deadline, cancel the macro and continue the already-advanced shadow champion. Record the exact cancellation reason. Once handed back, never retake control during that game.

For a roster of three, keep a three-troll joint selector rather than handing three trolls to the champion's two-troll claim-and-resolve loop. But evaluate it as an isolated component on identical three-troll states; do not bundle it with opening or roster changes.

**Expected size.** Conditional on a three-troll roster being independently justified, I would expect **3–8 points per game**, with an upper engineering ceiling around 10–15 from removing excess travel and idle work. I make **no rating claim** for this component alone.

**Falsification.** Drop it if an identical-state comparison shows any of:

- less than a 30% reduction in excess trip/no-command turns;
- paired final-margin gain below four points;
- a new >20-turn missed-progress episode;
- more controller hand-backs, target flips or illegal reservations than the champion.

## What not to do

I would not spend another experiment on:

- making the third troll arrive earlier;
- changing `OPENING_THIRD_MIN_NET`, `OPENING_THIRD_LATEST` or the seven-tuple menu in the old fixed-forest model;
- adding a banana planting heuristic only to command emission while the value model still sees a fixed forest;
- declaring fewer smoke “stalls” by relaxing the 20-turn threshold;
- reading another value number on the existing 24-map smoke or 200-map panel as if either were a holdout;
- placing the current bot on the ladder again.

Those edits either optimize a disproved proxy or hide the alarm without repairing the state transition that causes it.

## Machinery worth keeping

### Keep as reusable production components

1. **Exact small-deficit assignment.** `opening_assignment` exhaustively splits four resource deficits between two workers and keeps the earliest completion pair. It is useful as a lower-level macro evaluator or optimistic bound.
2. **Live re-root and abandonment.** Re-evaluating from the observed board every few turns is the right response to contested trees. It needs a shadow champion and exact progress deadlines, not removal.
3. **Resource shadow prices.** Putting fruit, iron and displaced wood on one opportunity-cost scale is the right interface. The prices must come from final-value replay over an explicit future forest, not a fixed-tree local rate.
4. **Joint command selection.** Reserving resources and combining all trolls' jobs jointly is necessary once three trolls exist. It should be tested as an isolated continuation component.
5. **Deterministic build chain.** Readable source, compacted source, SHA sidecars, exact token round-trip, compile checks, size checks, candidate/control generation and telemetry were all valuable and should remain mandatory.
6. **Failing our own bot honestly.** The pre-registered death conditions, control arm and `DEAD_AS_BOT` report made the real diagnosis possible. Keep that standard, while replacing the invalid control with the byte-identical champion incumbent.

### Keep only as heuristics or diagnostics

- `opening_resource_curve`: useful for candidate ordering and admissible/optimistic bounds, not a final value oracle;
- the seven third-troll tuples: useful as a smoke-sized seed set, not the legal search frontier;
- fixed `finish <= 110`: diagnostic only;
- the current smoke inactivity statistic: a mechanics alarm, not a score verdict;
- third-troll arrival time: explanatory telemetry only.

### Discard

- the mandatory Stage-2A generalist second-troll prelude;
- the current fixed-forest `future` cap as an admission objective;
- the current no-optimizer control arm as scientific evidence;
- any fallback that tries to undo an irreversible roster by merely returning control to the champion.

## Recommended decision

Do not revive `candidate-three-troll-optimized-v6-instrument.rs`. Use it as a regression corpus and source of reusable primitives. The active `chatgpt_1` build should be required to demonstrate, in this order:

1. optimizer-off is byte-identical to the champion;
2. fresh mechanics are 100% for both arms;
3. the action vocabulary includes `NO_PLANT` and `NO_TRAIN` and publishes the shadow-champion state;
4. the finite-forest forecast calibrates against exact replay;
5. a sealed holdout shows positive paired final margin;
6. only then ask whether any selected plan contains a third troll.

That sequence improves the bot by first making it impossible to lose to its own optimizer, then by searching the one resource transformation the old optimizer could not represent: spending a seed and a turn now to create bankable four-point wood later.