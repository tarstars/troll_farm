# Critical review of the Troll Farm project — 2026-09-05

## Assessment

Follow-up: `FIELD-CALIBRATION-RESULTS-2026-09-05.md` records the subsequent ten-game real-opponent
pilot, two replay-audit corrections, and the new `EVALUATION.md` contract. The review below records
the earlier read-only assessment; its statement that no gate/tooling changed applies to that
assessment, not the later implementation of its recommendations.

Further evidence: `NEXT-BOT-RESULTS-2026-09-05.md` records a tested productive fallback, its negative
competitive screen, and a specific suspect historical change. V368 beat the rank-seven agent on a
fresh map where V468 and both new profiles lost. V439 matched all 900 V368 commands in the screen
and differs from V468 only by V468's removed resource-denial bonus. This redirects confirmation
toward that decision instead of assuming that the new architecture or the latest baseline is best.

The main failure is the research and selection process. It has optimized a particular opening and
own-score curve on a small synthetic field without establishing that this objective predicts the
requested seventh place. There is useful code and unusually extensive reproducible evidence, but
the evidence does not justify treating the existing queue or gate as the path to the goal.

I initially resumed item 37 too mechanically. The owner's request to rethink the project supersedes
that continuation. No V631--V633 builder or candidate was created. The draft test is archived under
`/data/separate_troll_farm-working/analysis/2026-09-05-critical-review/`; it initially failed collection
because its intended builder did not yet exist. It has been removed from active test discovery.

This review makes no gameplay, gate, baseline, opponent, or platform-submission change. It pauses
the experiment queue and records the evidence needed to replace the current research plan.

## Verified current state

At 2026-09-05 04:32:46 UTC, a fresh read of the authoritative arena-room endpoint returned:

| field | value |
|---|---|
| live agent | V543, agent 6701731 |
| rating | 13.92 |
| rank | 155 / 177 |
| rollout | cached 100%, uncached 100%, not in progress |
| global rank seven | putibuzu, agent 6479779, rating 26.99 |
| global rank eight | tonigineer, agent 6505289, rating 26.94 |

The ordinary rank helper fetched the room successfully but could not load its optional `codingame`
package for the global table. A direct authenticated read of `getFilteredPuzzleLeaderboard` then
returned the top ten successfully. These were read-only requests, with no new games or submission.

The local published artifact is V543, while candidate development is compared against V468.
The last completed research commit is `16b40ee`. The neighboring singular-path repository
`../troll_farm` is at `370fa63cae12eda129ff5553c33a7086dfcb87c2`; it remains read-only. The
requested plural path was already documented as absent in the V543 report.

## Findings, ordered by impact

### 1. The acceptance rule does not express the user's objective

`panel_gate.py:4` explicitly excludes match outcomes and opponent score from selection. It accepts
only nonnegative own-score deltas at turns 100/200/final and at least +40 final. Neither early
checkpoint is a referee victory condition. Banked fruit is counted immediately, whereas fruit
spent on productive workers or trees disappears from that score until the investment repays.

The project's own `ECONOMY-GAP-2026-09-02.md:90` shows stronger orchard policies trailing the old
bot at turn 100 and overtaking later. Those are different opponent schedules, so they do not prove
that a particular candidate beats V468 head to head. They do contradict the rationale for making
early banked-score dominance a universal prerequisite for an investment strategy.

The +40 threshold was inferred from unpaired scores of differently rated players. No validated
conversion from +40 own points to seventh-place strength is established. A candidate can also
pass that formula while giving its opponents still more score.

Separately, the goal has drifted in the tooling: `CLAUDE.md:19` targets 25.40/top ten, and
`monitor_platform_agent.py:91` declares its objective true for score >=25 and rank <10. Rank nine
would satisfy that monitor but would not satisfy this thread's target. Completion must verify
seventh place or better for the exact submitted agent, after rollout and later confirmation.

### 2. The benchmark is not validated as a ladder-strength instrument

I recalculated these values directly from the archived 192-row TSVs, on the same eight maps,
both seats and twelve families:

| policy | final own score | W / D / L | change in W + 0.5D versus V468 |
|---|---:|---|---:|
| V468 | 247.25 | 177 / 3 / 12 | 0 |
| V543 | 358.21 | 163 / 1 / 28 | -15.0 / 192 |
| V546 | 378.48 | 166 / 1 / 25 | -12.0 / 192 |
| V564 | 418.72 | 174 / 1 / 17 | -4.0 / 192 |

V564's +171.47 own-score and +111.30 margin gains do not translate into more match points on
this panel. Against several weak families both policies already win every game: making those wins
larger dominates aggregate margin without demonstrating improved play around the ladder boundary.
V564 is a promising economic component, not a proven replacement. It did improve on V546 by eight
wins and +32.31 margin, so closing it solely for its early score deficit was also unjustified.

The earlier V543 holdout is an even clearer warning. On sixteen fresh maps it gained about 96
margin, but outcomes changed from 341/2/41 to 340/4/40: identical total W + 0.5D. It subsequently
finished the platform rollout at 13.92/rank 155. New maps did not correct the opponent mismatch.

Named proxies must not be confused with the real ranked bots. The imported
`norxondor_native.rs:1` calls itself a research reconstruction. V564's sixteen local wins against
that family are not sixteen wins against the actual rank-two agent. Replica fidelity must be
measured before a proxy supplies evidence about a particular ranked player.

### 3. The sample structure is much narrower than the game counts suggest

The 24-game smoke is one map, not 24 independent maps. The full 192-game development panel is
eight maps, not 192 independent map draws. Both seats and repeated opponents add coverage but do
not remove shared-map dependence. Statistical uncertainty must preserve that grouping.

V610 passed the one-map smoke at +40 final and failed the eight-map panel at -42.01. V609 was
screened out at +39.83 despite having two fewer losses than V610 on that smoke. That 0.17-point
cutoff is not a justified economic distinction on one repeatedly used map.

The portfolio inventory found 53 eligible panel files and 40 distinct behaviors on the same eight
maps. These are development data. Leave-one-map-out selection among policies already designed
using the full development set is useful stress testing, but is not a fully independent validation
of the complete design process. A fresh-map holdout also needs independent opponent coverage.

### 4. The experiment design often defeats the mechanism it claims to test

V587 correctly observed that rank seven and eight overwhelmingly use two workers and recommended
an integrated crop lifecycle. V619 onward then preserved V468 through turn 100 and repeatedly tried
to fund additional workers afterward. This tests a late transition from V468's already-spent
opening; it does not test the leaders' early orchard economy or establish that two workers cannot
produce it.

The repeated conclusions should be narrowed to their evidence: particular late controllers failed
on specific maps. They do not close producer-first economies, mature orchards, adaptive worker
choices, or an entire strategic family. A hindsight portfolio bound under the same early-score
constraints does not rescue those constraints or prove that the unconstrained policies are useless.

Item 37 would alter the opening, but continuing the same three-arm builder/smoke loop before
fixing selection would still be the wrong priority.

### 5. I reproduced a real economic-priority defect in the latest controller

In `candidate_v630_producer_bridge_speed_fourth_module.rs:3989`, the producer's initial harvest
path filters fruit through `crop_needed(kind)`. That predicate counts planted trees against a crop
quota; it does not ask whether banked fruit is still needed for training. With two owned lemon
trees, lemons are excluded from this priority path even if seven banked lemons are missing.

A diagnostic Rust fixture compiled against an instrumented copy of the exact V630 source showed:

- a ripe owned lemon under the producer, with an active seven-lemon deficit;
- two owned lemon trees, reaching the ordinary quota;
- an unneeded ripe banana one cell away;
- `worker_goal` chose to harvest the banana; unrestricted deficit-first harvesting chose the lemon.

The unrestricted fallback can still harvest lemons when the earlier path finds nothing, so this is
a priority inversion, not a total prohibition. Its frequency and full-game impact have not been
measured. Nevertheless, it invalidates the strong statement that the implemented producer path is
economically correct and only chronology remains. The fixture is at
`/data/separate_troll_farm-working/analysis/2026-09-05-critical-review/harvest-priority-probe.rs`;
the compiled probe passed, asserting the observed erroneous choice.

Another inspected weakness is `chop_cell` at line 4102: its main value uses full tree size divided
by travel, with chopping time only a later tie-break and no carrying-capacity clipping. The referee
caps collected wood by free carry capacity. This does not prove a particular alternative scorer
wins, but the current score cannot justify claims of optimizing collectible wood per worker-turn.

### 6. Tests and packaging checks have been credited beyond their scope

The sixteen V628 tests mostly check source strings, constants, substitutions, emission, size, and
one standalone compile. Those checks are useful for reproducible construction. They do not verify
that a worker harvests the right fruit, completes a crop lifecycle, banks the predicted payout, or
improves competitive outcomes. The defect above survived the reported 348-test suite.

The runner times an in-process `policy.commands()` call. This omits process launch, protocol input,
and first-output startup. V543's seven first-action timeouts remain a separate unresolved deployment
concern; source-size reduction was a hypothesis, not proof of their cause. They are also not
sufficient evidence to explain the entire ladder deficit.

The working tree has 1,013 candidate Rust files and 102 version builders. Generated historical
artifacts are valuable, but chains of textual substitutions and multiple complete controllers near
the source limit make new behavior expensive to review. The next active implementation should
have one editable modular source and a deterministic standalone export; historical copies can stay
archived. Refactoring alone would not improve the ladder.

### 7. The neighboring project is useful evidence, not a substitute authority

It contains the referee, replay tooling, historical opponents, strategy write-ups, and relevant
failed experiments. Its September 4 instrument audit independently recognized overused test sets
and poor local-to-ladder calibration; the sealed-holdout task addresses both map reuse and opponent
lineage. These findings are directly useful here.

Its documents also contain conflicting historical goals and provisional margin-to-rating rules
based on very few observations. They must not be copied into this project's acceptance criteria.
Neither aggregate margin nor win-only statistics automatically solves a misrepresentative opponent
pool. Count draws explicitly, retain opponent-specific results, and validate against actual field
evidence. Nothing in the neighboring repository was modified or run as a coordination workflow.

## What remains trustworthy

The official referee rules, immutable source hashes, archived command streams, real final outcomes,
paired same-map experiments, and readable/compact equivalence checks are valuable. Several
mechanism findings survive this review: carrying capacity limits mature wood payout, serial fruit
funding has an opportunity cost, traffic can disable workers, and late deployment often cannot repay.
None establishes a universal fixed roster or planting schedule.

The correct reset preserves these assets and discards the unsupported inference from a passing
local own-score curve to top-seven strength.

## Revised direction

1. Make the explicit success condition the verified rank of the exact live agent, seventh or
   better after evaluation and confirmation. Rating is contextual evidence, not a fixed substitute.
2. Calibrate evaluation before new candidate tuning. Compare a small set of archived policies with
   known platform results, including V468 and V543, against varied adaptive opponents. Identify
   which local measures distinguish them and where they disagree with the real field. Use real
   ranked-agent evidence where available; fixed replay commands are diagnostics after divergence,
   not an adaptive opponent. Do not claim calibration if there are too few independent observations.
3. Retain the old panel as development/regression data. Build separate unseen-map and opponent
   tests. Track W/D/L, W + 0.5D, margin, failure rate, and opponent-specific changes with map-grouped
   uncertainty. Keep t100/t200 curves as diagnostics rather than universal pass requirements.
4. Audit finalists as executable policies. Test actual crop/worker transactions, resource
   accounting, reservations, movement, and protocol startup before drawing strategic conclusions.
5. Then choose one coherent economy. The initial architectural hypothesis is an integrated
   controller that jointly schedules harvesting, planting, felling and banking, values collectable
   payout and complete trips, and buys workers only when the full continuation repays. Compare it
   with both the reliable two-worker policy and the best dense policy. Do not hard-code a third
   worker or a turn-100 prefix solely to satisfy the old selector.
6. Use the user's existing publication authorization for candidates supported by the revised
   evidence and deployment checks; archive exact identity and mature outcomes. A ladder failure
   must update the evaluation model, not merely generate another local heuristic.

The immediate next work is measurement calibration and an explicit replacement evaluation design,
not V631 and not a blind V564 publication. Rank seven remains unachieved.

## Source integrity

Production hashes remain `bot.rs`:
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`, and `submission.rs`:
`922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
The neighbor's existing modified stats file and untracked panel JSON remain untouched.

Relevant retained reports: `ECONOMY-GAP-2026-09-02.md`, `ADAPTIVE-R1FA-RESULTS-2026-09-04.md`,
`V543-MATURE-PLATFORM-RESULTS-2026-09-04.md`, `V564-V565-HIGH-CAPACITY-THIRD-RESULTS-2026-09-04.md`,
`V587-RANK7-GAP-RESULTS-2026-09-04.md`, `V609-V611-CARRY-ALIGNED-MATURE-WORKER-RESULTS-2026-09-05.md`,
`V612-CROSS-LINEAGE-PORTFOLIO-RESULTS-2026-09-05.md`, and
`V628-V630-STOCK-LIGHT-PRODUCER-BRIDGE-RESULTS-2026-09-05.md`.
