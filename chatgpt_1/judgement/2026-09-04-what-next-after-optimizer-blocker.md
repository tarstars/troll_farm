# What to do after the first PLANT-aware optimizer failed

Date: 2026-09-04  
Task: `20260904-start-game-optimizer-build`  
Scope: judgement only; no build, panel, ladder, platform, Arena or cluster action

## Verdict

**Close the current build card. Do not patch its constants.** The design remains worth pursuing, but the next step must be a narrower, offline paired-continuation experiment in which the unchanged champion really is the baseline and the opening it already knows how to play cannot be damaged.

The single next experiment should be:

> **Freeze the champion through its own second-troll training, disable every further `TRAIN`, and use exact paired replay to ask whether a small near-shack orchard rotation can beat the unchanged champion by game end.**

The experiment searches `PICK`, `PLANT`, `CHOP`, `DROP`, movement targets and event waits after the champion's second troll exists. It may choose no plant. Every candidate is replayed to turn 300 under the same opponent scenario as a continuously advanced champion baseline. There is no special early-second prelude and no third-troll question in this experiment.

My working rating estimate is **about +2.5 points, with a wide 0 to +4 range**, if the near-orchard mechanism is real. This is a planning prior, not a calibrated conversion from local score to ladder rating. The experiment is wrong at the mechanism level if the paired final-margin lower 95% bound is not above zero, if paired own score is negative, or if the optimizer normally chooses the no-plant champion. It is too small for an external ladder test if its mean paired final-margin gain is below roughly 15 points or its honest rating prior remains below the observed 2.2-point one-read variability.

## Why this one experiment

The new orchard read gives a concrete mechanism rather than a general hope about planting:

- at turn 108, the median game still has 24 wild wood, but the surviving trees are at median door-distance 13;
- no wild tree remains within four steps from turn 75 onward;
- a chop-3, carry-4 worker earns about 0.5 points per worker-turn at distance 13;
- a near mature banana can be converted at 3.2 points per worker-turn, and the full plant-to-grow-to-fell chain is about 1.73;
- planting does not beat a nearby standing wild tree, so the orchard is a **near reserve**, not a free value engine;
- a large late-felled orchard is bad because the opponent raids it, so the useful policy is small, near, banana-heavy and felled around maturity.

This says exactly what should be measured: whether reserving near wood after the champion has secured its normal second worker produces more final value than the champion's own continuation. It does not justify another early roster change, another fixed-tree forecast, or a thirty-tree endgame stockpile.

The search may examine all species for completeness, but banana should be the first ordering choice because it yields the same four wood as every mature species at only six health, costs no training resource, and has the best measured plant-to-fell value. Water-adjacent cells must be treated as scarce: the median map has only two within two steps and five within four.

## 1. What should we do next?

Run the **paired champion-prefix orchard-only oracle** described above, offline on development maps and fixed opponent scenarios.

The two worlds must begin from the same exact state and the same champion memory:

```text
A: unchanged champion -> turn 300
B: unchanged champion through its own second TRAIN
   -> searched near-orchard macros
   -> continuously advanced shadow champion -> turn 300
```

The branch point is after the champion's own second troll is trained. This is deliberately conservative. It prevents the experiment from getting an apparent orchard result by changing the roster, delaying training, or replacing the champion's opening. `NO_PLANT` is always legal. The third troll is disabled.

Every irreversible planting macro must include the seed, worker travel, exact growth release, expected raid, felling, carry and banking work. Candidate and baseline use common maps, seats, starts, opponent scripts and seeds. The decision statistic is paired final score margin; paired own score is a mandatory guard.

### Expected size

Working prior:

- final own-score or margin gain: **roughly 10 to 25 points per game** on maps where the near reserve is used;
- ladder effect: **about +2.5 points**, wide range **0 to +4**.

The rating number is explicitly uncertain because the project has no positive-side calibration. The mechanism is nevertheless the only current one with a plausible effect near or above the one-read ladder variability.

### Falsification

Stop the orchard-optimizer line if any of these occurs:

1. the optimizer-off path differs from the champion before or after the branch;
2. the champion's second troll changes in talent or training turn on any case;
3. the paired final-margin lower 95% bound is not above zero;
4. paired own-score lower bound is negative;
5. the no-plant champion is selected on most maps;
6. the gain disappears under the high-raid scenario;
7. exact replay shows wood overstatement above the already adopted 1.5-times bound.

A positive but small result may be scientifically real and still not be worth a ladder slot. Below about +15 paired margin, keep it as a measured component rather than claiming a detectable rating improvement.

## 2. Does the Stage-2A prelude finding change my diagnosis?

**Yes, it makes the diagnosis more precise. It does not rescue the candidate.**

My blocker correctly identified the immediate failure: the build priced a planting worker-turn with a scalar opportunity rate instead of comparing the whole discrete champion continuation. That shortcut allowed locally profitable banana plants to postpone the second worker. The smoke showed the second troll moved to the hard turn-35 fallback on 14 of 24 maps.

chatgpt_2's analysis identifies the broader architectural class: an irreversible second-troll purchase changes the roster and then hands that state to a continuation that was validated for another roster. The turn-35 fallback in my build is the same class of defect. It is not a harmless delay that can be repaired after hand-back; resources and the chosen talents have already changed.

However, it would be wrong to say the inherited prelude explains every alarm in my smoke. My five flagged maps are not chatgpt_2's five common candidate/control maps. My smoke includes both patterns:

- maps where the candidate delays or changes the second troll before hand-back;
- maps where the candidate and resident have the same early second troll but the new planting schedule still produces a long no-command interval.

Therefore the corrected diagnosis is:

> **The custom second-troll prelude and the scalar planting valuation are two manifestations of one missing invariant: no irreversible action may replace the champion unless the complete alternative continuation has already beaten it. A progress alarm is also needed, but it cannot undo a bad `TRAIN` or `PLANT`.**

The harness's `stalled` flag must also be described correctly. It is a relative long-inactivity alarm, not a crash, referee termination or automatic loss label. Both arms can answer all 300 turns, and a flagged arm can outscore the resident. The alarm remains a valid fail-closed mechanics condition because it says the new controller has created an unexplained long period with no productive command. It must not be translated into “the game was lost outright.”

### Where the fix belongs

The primary fix belongs **inside the optimizer before commitment**:

- champion is the exact incumbent;
- its opening and internal state are advanced continuously;
- no custom second-troll prelude runs first;
- an irreversible alternative is taken only after paired continuation replay.

A progress invariant belongs **around execution and hand-back** as a secondary safety mechanism. Each active macro must name its next observable event and deadline: position reached, inventory changed, tree health reduced, crop released, bank increased or training completed. Missing the deadline cancels the macro and returns to the already advanced champion. That prevents silent inactivity, but it is not the economic test for buying a troll or planting a tree.

## 3. Is the failed build repairable?

**The accepted design is repairable; the current build card and candidate are not. Close them.**

The card had a pre-registered 24/24 mechanics condition and the candidate produced 19/24. Continuing to edit it under the same card would turn a failed gate into tuning on development data. The correct implementation is materially different enough to need a new card.

A valid successor would change the following:

1. remove the custom early-second selector and hard turn-35 fallback;
2. keep the champion command stream byte-identical through its own second `TRAIN` in the first experiment;
3. disable a third troll entirely;
4. carry or continuously advance the real champion continuation state in the candidate world;
5. cache the baseline champion continuation for each branch state;
6. use the fast finite-forest model only to generate a small Pareto frontier;
7. exactly replay the top frontier plans against the cached champion under the fixed opponent scenarios;
8. add per-macro progress deadlines and one-way fallback.

This is not a constant change. It is the exact-reranking stage that the design specified and the first build omitted.

### Cost

The economic cost is manageable offline and unproved online.

With four opponent archetypes and two seeds, one candidate plan needs eight candidate continuations. The champion side can be cached for a shared branch state rather than rerun for every plan. Re-ranking eight plans therefore means roughly 64 candidate continuations plus the cached baselines for each map. That is appropriate for an offline mechanism experiment.

A naive in-bot implementation would not fit the time budget merely because the reduced A* engine once ran in 378 ms. Full paired continuations and scenario replay are different work. The next card should therefore be **offline first**. Only after it finds a stable positive policy should the project either:

- distil the recurring policy into a compact rule; or
- benchmark a very small top-K exact re-ranker for the 850 ms first-turn budget.

The existing 77,043-unit source also leaves limited room under 100,000. Reusing the existing champion implementation and keeping exact multi-scenario replay outside the submitted bot is more credible than embedding a second simulator.

So the repair cost is one new implementation round for an offline paired oracle and one development measurement. It should not include a panel, fresh holdout or ladder until the offline mechanism passes.

## 4. What can we actually detect?

The project should distinguish **one-read ladder variability**, **repeat-read ladder precision**, and **paired simulator precision**.

### One ladder hour

The identical champion file has read 17.04 to 19.23, a range of 2.19 and sample standard deviation 0.82. Therefore a single one-hour candidate reading cannot settle a one-point or even many two-point claims. Any sub-2.2 statement from one reading is narrative, not measurement.

The 2.19 figure is an observed range, not a law of nature or an irreducible floor. Interleaving repeated candidate and champion reads can average some random variation. Under the optimistic assumption that readings are independent with standard deviation 0.82, roughly six readings per arm are needed for a two-sided 95% interval with about one rating point of half-width, and about 21 per arm for half a point. Matchmaking drift and time correlation can make the real requirement larger. The current five champion observations are too few to certify the ideal calculation.

### Exact paired simulation

The exact simulator can resolve score differences far smaller than 2.2 rating points because it uses the same map, start, seat, opponent and seed for both arms. It can answer causal questions such as whether one orchard schedule produces five more banked points under the model. It cannot by itself tell us that five local points equal a particular ladder gain, and the repeatedly used smoke and 200-map panel are development data rather than proof of generalisation.

### Practical consequence

**Most micro-changes are unmeasurable on the ladder with the current one-hour habit.** That includes many target-score tweaks, deadlines, stickiness rules and one-tree heuristics. We should not spend a ladder slot on them individually.

This does not require stopping all bot work and doing only instrument work. It requires a stricter split:

- use exact paired replay to reject or understand small mechanisms;
- use a sealed fresh holdout to test generalisation after source and thresholds are frozen;
- reserve the ladder for candidates with a plausible effect above about 2.2 rating points;
- use an interleaved multi-read block, not one isolated reading, for the finalist.

The nine-point gap to the top four makes the same point strategically. We need changes with a credible double-digit final-score mechanism, not many half-point ladder guesses. The near-orchard reserve is still worth one clean experiment because it may move worker productivity from about 0.5 to 1.7 points per turn after the near wild forest disappears. If that exact paired experiment is small or negative, the honest next priority should become instruments and new strategic mechanisms rather than further tuning of this optimizer.

## Owner-facing decision

The one decision I recommend is:

> **CLOSE the current optimizer build and charter one offline champion-prefix orchard-only paired experiment.**

Do not reopen the early-second or third-troll line. Do not put the failed candidate on a panel or ladder. Let the active orchard read finish its calibration, but the experiment above can be specified now because its architecture is independent of the final parameter table.
