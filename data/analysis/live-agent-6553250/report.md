# Live agent 6553250: recovery and follow-on experiments

Date: 2026-07-16

## Outcome

The live Legend champion is now reproducible from the repository. The exact recovered source
compiles, its formatted copy produces the same command stream, and the submission helper now
defaults to that exact artifact. No arena submission was made.

The first `idle-harvest-off` smoke was correctly **parked** because it did not isolate the
removed behavior. A follow-on instrumented study now closes the ablation as **REJECT: keep the
live idle-harvest fallback**. The branch is rare in controlled field games, but exact-state and
paired local evidence show positive value when it actually selects an action. No arena
submission was made.

## Sources under test

| bot | artifact | bytes | SHA-256 |
|---|---|---:|---|
| baseline | `cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs` | 90,133 | `09fac1fefa24eac657dba16a75d802eee38e1269f4aa44413e1ca103df36fe7a` |
| candidate | `cgauto/submissions/candidate-agent6553250-idle-harvest-off.min.rs` | 90,120 | `492b6b6a8237c6fa3dd7b37bd41133f18baaf254705e778ffef50e79b224ac8d` |

The generator performs exactly one constructor replacement: the live default changes from
`tuned_carry_regeneration_transit_idle_harvest()` to
`tuned_carry_regeneration_transit()`. It does not alter the orchard wrapper or any other policy.

## Corpus evidence

The local corpus contains 161 games for agent `6553250`: 84 wins and 77 losses. All 161 replay
announcements match `yamo-carry-regen-transit-idle-harvest-rust`.

Across those games:

- 71 games contain at least one `HARVEST` command;
- 341 `HARVEST` commands appear in total;
- the median harvest turn is 70;
- 36 harvests occur after turn 250, spread across 11 games.

Those commands do not identify the policy branch that selected them. The inner idle-harvest
path is gated by endgame state and by all ordinary candidates being idle. Independently, the
outer `SecureOrchardBot` can force the starter to harvest the protected apple mother. Therefore
late `HARVEST` counts alone cannot measure the ablated mechanism.

## Controlled smoke protocol

`cgauto/field_panel.py` used authenticated `TestSession/play` games, which do not alter the
arena submission. It alternated baseline and candidate against five fixed Legend agents, one
random map per cell, for ten games total. The saved panel was then enriched from authenticated
read-only replays so turn counts and command traces are retained.

| opponent | baseline | candidate |
|---|---:|---:|
| delineate | 212-409 L | 202-242 L |
| wala | 184-166 W | 260-209 W |
| escdemon | 156-158 L | 92-95 L |
| norxondor | 175-375 L | 160-283 L |
| laconic | 184-176 W | 275-297 L |

| aggregate | baseline | candidate |
|---|---:|---:|
| record | 2-3 | 1-4 |
| mean score | 182.2 | 197.8 |
| mean opponent score | 256.8 | 225.2 |
| mean margin | -74.6 | -27.4 |
| mean wood | 45.2 | 49.0 |
| mean fruit | 1.4 | 1.8 |

The records and margins point in different directions, as expected from five unpaired random
maps. More importantly, none of the baseline games issued a harvest after turn 250. Baseline
harvest turns were `3`; `3,7,11`; none; `5,13`; and none. Early harvests are ordinary opening
or orchard activity and are not evidence that the endgame fallback fired. The sparse-map
endgame condition and the wrapper's forced harvest make command-only attribution ambiguous.

## Follow-on causal study

The diagnostic artifact
`cgauto/submissions/diagnostic-agent6553250-idle-harvest-probe.min.rs` adds stderr-only telemetry
at three separate layers:

- `@IH_CAND`: the inner fallback produced candidates;
- `@IH_SELECT`: one of those candidates won the inner assignment;
- `@IH_ORCHARD_FORCE`: the outer wrapper independently forced a mother-tree harvest.

It is 90,826 bytes (SHA-256
`3ada15b311ee58f798401dd8e9e3231d0c7dee2bc3055dcef99b808efce82c2c`). On a fixed 300-view
input stream its stdout is byte-identical to the exact live baseline.

### Identical-state fixture

The first baseline/candidate action divergence occurs at turn 280 on the same state:

- live baseline: `HARVEST 0`;
- idle-harvest-off: `WAIT`;
- probe: `@IH_SELECT t=280 unit=0 command=HARVEST 0`.

Rolling both policies forward from that state gives baseline 5 points versus candidate 0. The
fallback harvests and banks an apple, converts the seed into one wood, and later banks another
apple; the ablation stays idle.

### Paired local simulation

Forty deterministic seeds were played with seat swaps. This is mechanism evidence, not an arena
predictor—the historical self-play calibration failure still applies.

| measure | result |
|---|---:|
| seeds with an inner selection | 5/40 |
| mean paired margin, all seeds | +0.775 |
| mean paired margin, activated seeds | +6.2 |
| activated-seed paired margins | +6.5, +8.0, +8.0, +4.0, +4.5 |

Every activated seed favored the live baseline. Two other seeds produced 138 and 134 outer
orchard-forced harvest events with zero inner selections, confirming that the probe separates
the mechanisms that replay command counts had conflated.

### Controlled platform activation sample

The probe then played ten more controlled `TestSession/play` games—two against each fixed
top-five opponent. It produced **0 inner candidates and 0 inner selections**. One laconic game
produced 140 outer orchard-forced harvests, from turns 22 through 300 on alternating turns.
Thus the inner fallback is rare in this field sample, while the outer wrapper can be highly
active and is demonstrably independent.

Artifacts:

- `data/analysis/live-agent-6553250/idle-harvest-local-study.json`;
- `data/panels/top5-idle-harvest-telemetry.json`.

## Final verdict and next experiment

The original smoke remains an infrastructure pass whose 1-4 candidate record must not be
extrapolated. The follow-on causal result is sufficient to reject the removal: it deletes a rare
fallback that is positive in every activated paired case, with no observed negative activated
case. Keep the exact live baseline and do not submit `idle-harvest-off`.

The next candidate search should move away from idle harvest. Decode repeated losses against
delineate, wala, and norxondor, then select a mechanism that fires frequently and explains a
material score component before constructing another one-site candidate.

Raw result: `data/panels/top5-idle-harvest-off-smoke.json`.

## Repeated-loss decomposition

The requested follow-on examined all 40 corpus games against delineate, wala, and
norxondor_gorgonax (12 wins, 28 losses). The reproducible output is
`data/analysis/live-agent-6553250/matchup-loss-analysis.json`, generated by
`cgauto/live_loss_analysis.py`.

The repeated loss is a late sustainable-wood conversion failure, not an opening failure:

- 23/28 losses start ahead on wood at turn 100 and finish behind at turn 300;
- mean wood gap moves from +9.6 at turn 100 to -6.3 at turn 200 and -28.4 at turn 300;
- all 28 opponents successfully plant at least 20 trees and harvest at least 20 fruit;
- 26/28 opponents land at least 60 chops, and 22/28 train at least two extra trolls;
- live lands 138.3 chops for 53.3 final wood, while the opponents land only 117.1 chops for
  81.2 wood. Mean per-game wood/chop is 0.418 versus 0.773.

Our own final wood and chop count are nearly flat between wins and losses. The decisive variable
is whether the opponent turns a renewable harvest/plant loop into cheap local trees and then
wood. This explains the turn-100 lead reversal and rules out raw chop volume as the next target.

The outer secure orchard is not frequent enough to be the primary repeated mechanism. A broad
three-cycle signature occurs in 4/161 historical games; only two have at least ten consecutive
cycles. Those two sustained cases split one win and one loss. The additional controlled telemetry
game is a large loss, so the wrapper remains worth monitoring, but a blanket ablation is not
supported.

## Sparse sustainable-farm candidates

The recovered source already contained a dormant `scarce_farming` mother/crop loop for maps with
at most 14 initial trees. It was tested before inventing a new economy or training policy.

| candidate | exact artifact | activated local seeds | paired margin | wood delta | result |
|---|---|---:|---:|---:|---|
| isolated dormant loop | `candidate-agent6553250-sparse-farming-on.min.rs` | 17/60 | -47.5 | -11.9 | reject |
| work-conserving repair | `candidate-agent6553250-sparse-farming-work-conserving.min.rs` | 17/60 | -32.5 | -8.1 | reject |

The isolated artifact is 90,168 bytes, SHA-256
`01bb1f6ee69694e74379147aa6dc4520be716a325977720416b108910a9707dc`. Every activated seed lost;
all 43 inactive dense-map seeds were exactly neutral. Its trace exposed a dormant implementation
bug: when a crop existed or an ordinary chop was available, the assigned farmer returned no
candidates, adding about 115 waits and deleting about 61 chops per activated game.

The separate work-conserving repair is 90,386 bytes, SHA-256
`7c72a00ba14bcfe4d70af4b1112922ec4d1c4e16197e71d684852f68e730103e`. It releases the farmer
back to the live chop loop and keeps idle harvest intact for every non-farmer. Dense maps again
remain exactly neutral. The repair cuts the damage but still goes 1-16 when activated: roughly
two added harvest/plant cycles displace 37.7 chops, add 16.2 moves and 22.4 waits, and lose 8.1
wood. The planted crop also becomes wood available to the opponent.

This local gate is explicitly not an arena predictor. The reason to stop is narrower: both
variants directly worsen the exact score component they were built to improve, in every dense
map they are byte-behavior neutral, and the repair still has a clear negative action/wood
mechanism. No controlled platform games and no arena submission were made.

Artifacts:

- `data/analysis/live-agent-6553250/sparse-farming-local-study.json`;
- `data/analysis/live-agent-6553250/sparse-farming-work-conserving-local-study.json`.

## Wood-conversion field telemetry

`cgauto/make_wood_conversion_probe.py` produced an exact behavior-neutral diagnostic artifact,
`diagnostic-agent6553250-wood-conversion-probe.min.rs` (91,058 bytes, SHA-256
`e03aec1a63350c5d96c8db07040e7582e6c4c53515d3576fba687765e738fa33`). Its stdout is
byte-identical to the live source over a fixed 300-view stream. Stderr records state, selected
tree, unit stats, travel, free carry, fell yield, and orchard overrides.

Ten controlled games, two against each fixed top-five opponent, are stored in
`data/panels/top5-wood-conversion-telemetry.json`. The sample went 2-8, with mean score 171.8
versus 232.0 and mean final wood 42.6 versus 49.4. Across the live bot's 1,744 chop actions:

| tree kind | chop actions | realized wood | wood/chop |
|---|---:|---:|---:|
| apple | 414 | 60 | 0.145 |
| banana | 460 | 183 | 0.398 |
| lemon | 494 | 113 | 0.229 |
| plum | 376 | 72 | 0.191 |

The probe rules out the obvious carry-detour hypothesis. It observed 429 units of nominal wood
not collected on partial fells, but only 10 were potentially recoverable by banking before the
fell. Another 408 were unavoidable because the tree's final size exceeded the unit's maximum
capacity; 11 had other causes. Only 13 partial fells began with any cargo. Earlier banking would
therefore add travel while recovering at most about 2% of the observed uncollected wood.

The stronger split is unit capability. Starter unit 0, always chop 1/carry 1, spent 845 chop
actions for 114 wood (0.135/chop). Trained trolls spent 899 actions for 314 wood (0.349/chop).
This explains much of the aggregate conversion gap: the live bot spends nearly half its chop
turns through the weak starter, while the repeated-loss opponents commonly field more trained
trolls. It does not by itself justify another troll—the project history shows that extra workers
can lose more to crowding and supply than they gain—but it narrows the next safe lever to
unit/target matching.

## Focus-bonus ablation

The live chop score contains a denial bonus for its chosen lemon/plum focus kind, weighted by
distance to the opponent shack. Because banana chops had the best raw yield, the smallest
target-choice test removed only that bonus. The exact candidate is
`candidate-agent6553250-focus-bonus-off.min.rs` (90,131 bytes, SHA-256
`b81486311b241da6397dfca29657bd424e9172ff70fbea37479deac7e44157a6`).

The 60-seed paired local self-harm screen was effectively neutral: mean paired margin -0.19,
wood -0.07, and 24 wins/7 ties/29 losses. A separate behavior-neutral probe batch happened to
go 5-5 with 0.275 wood/chop, versus 2-8 and 0.245 for the baseline probe batch. Those platform
maps were random and unpaired; the apparent improvement is an escalation signal, not a causal
comparison. It also shifted the observed chop mix toward apple and away from banana, so it did
not validate the intended mechanism.

The balanced standard-source promotion smoke then ran two repetitions against delineate, wala,
and norxondor (`data/panels/core3-focus-bonus-off-smoke.json`):

| bot | record | mean score | mean opponent score | mean margin | mean wood | mean opponent wood |
|---|---:|---:|---:|---:|---:|---:|
| exact baseline | 3-3 | 209.8 | 198.3 | +11.5 | 51.8 | 47.2 |
| focus-bonus-off | 0-6 | 162.0 | 312.7 | -150.7 | 39.7 | 67.0 |

This still is not a paired-map arena estimate, but a candidate that goes 0-6 after a neutral
local screen has failed the conservative promotion gate. Removing the bonus also exposes the
opponent's renewable lemon/plum supply, matching the loss mechanism that motivated the study.
Decision: **REJECT `focus-bonus-off`; preserve the full live denial bonus.** No arena submission
was made.

## Final decision and next move

Keep exact live agent `6553250`. Reject all three tested change families: idle-harvest removal,
sparse farming, and global focus-bonus removal. The telemetry also closes the early-banking
branch.

The proposed unit-role isolation was built next. Candidate
`candidate-agent6553250-focus-bonus-capable-only.min.rs` is 90,189 bytes (SHA-256
`0170a3443d2622097df5a531ae36804d81a038962342e85806f094572246ad08`). It keeps the full
focus bonus whenever chop power or carry capacity exceeds one, and removes it only for a
chop-1/carry-1 worker. Capability, rather than unit id, makes the policy correct under seat
swaps and for rare fallback-trained weak workers.

The 60-seed paired local gate ran with eight workers and failed:

- mean paired margin: -1.21 (approximate 95% interval -2.40 to -0.02);
- mean wood delta: -0.31;
- 13 wins, 18 ties, and 29 losses;
- mean action delta: -1.59 moves, +1.61 waits, and -0.04 chops.

The score loss is almost entirely wood: subtracting four times the wood delta leaves only +0.025
points/game. Thus the intended starter freedom did not improve conversion even in the local
self-harm test; it slightly reduced completed wood cycles. This gate is not an arena predictor,
but a directionally negative candidate does not qualify for scarce remote evidence. Decision:
**REJECT `focus-bonus-capable-only`; run no platform games.** Raw result:
`data/analysis/live-agent-6553250/focus-bonus-capable-only-local-study.json`.

Both global and role-limited focus removal are now closed. The next investigation should be
read-only: extract actual train turn/spec and subsequent work share from the 161 historical live
games before changing training. Existing field telemetry shows trained workers convert much
better, but it does not yet distinguish selection effects from a causal spec advantage.

## Ten-idea training-policy sweep

Ten exact one-field variants then tested the remaining opening-policy knobs: preferred/max
carry, preferred/max chop, strict carry floor, shorter/longer extra ETA, earlier/later hard
deadline, and movement tie-breaking. Every Stage-1 screen used the same 60 paired seeds and
eight workers. Only `train-extra-eta8` and `train-cap-chop2` had positive raw means, so both were
confirmed over 200 seeds.

`train-extra-eta8` flipped from +1.125 at 60 seeds to -0.480 at 200, with -0.125 wood.
`train-cap-chop2` retained a +1.025 raw mean, but failed robustness: 35 wins/112 ties/53 losses,
-0.040 wood, approximate 95% interval [-1.73,+3.78], and a -0.703 5%-trimmed mean. Two extreme
seeds supplied +374 of its +205 total margin. Neither qualifies for field evidence.

The other eight variants were negative or effectively inert. Full table and interpretation:
`data/analysis/live-agent-6553250/training-policy-sweep.md`; machine-readable aggregate:
`data/analysis/live-agent-6553250/training-policy-sweep-summary.json`.

Decision: **NO WINNER; keep the exact live training policy.** The sweep used zero controlled
platform games and zero arena submissions. Stop tuning isolated opening constants; the next
candidate must introduce a measured structural mechanism rather than another parameter change.

## Renewable-supply iteration

The structural follow-on measured exact live self-play before changing policy. Shared tree count
falls from 16.23 initially to 1.55 at turn 100, 0.48 at turn 150, and 0.18 at turn 200. First
exhaustion occurs at median turn 81.5; 86/116 exhausted sides still have fruit and 69 have banana.
Live already plants that stock (12.89 plants/game, median last plant turn 113.5), so moving stored
fruit earlier cannot create more total supply.

Six protected mother/crop refinements were then tested: late activation, true-exhaustion
activation, one-generation release, banana-only renewal, mother-first liquidation, and one-tree
ripening overlap. All lost wood. The broad loop was -11.77 margin/-2.89 wood; the most selective
mother-first pulse improved to -1.27/-0.32 but still produced 6 wins versus 14 losses. The
200-seed timing-only pre-seed was exactly balanced at 21W/158T/21L, +0.06 margin/+0.02 wood, with
no change in total PICK or PLANT.

Decision: **NO RENEWABLE-SUPPLY CANDIDATE; no field games.** Creating a shared mature mother costs
more private wood than its crop returns. Full report:
`data/analysis/live-agent-6553250/renewable-supply-study.md`.
