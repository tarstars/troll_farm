# Opening solver Stage 2 design review

- Reviewer: `chatgpt_1`
- Task: `20260903-opening-solver`
- Evidence pin: `05ab7d3bebe9878f73cb80199923c1b11b26dfd5`
- Scope: design review only; no search, ablation, ladder, platform, cluster, host, or author-file action

## Verdict: ACCEPT-WITH-EDITS

Stage 1 is strong enough to charter Stage 2. The verified result is substantial: with orchard 6's roster, the solver reaches the third troll at median turn **70** versus **88.5**, a median gain of **21 turns** on **292** map-seats; it is more than ten turns earlier on **74%**. The edits below are required before this becomes an in-bot objective or a claim about live opponents.

## 1. Optimise a frontier of full roster states, not one chop sum and not one fixed `c`

The planner should retain non-dominated plans described by:

- completion turn;
- the full talents and arrival turn of every troll;
- bank, carried resources, and unit positions;
- the exact planted/wild-tree state at completion.

Within the **same full roster**, earlier completion remains the first key. Across different rosters, completion turn cannot be the whole objective: the measured free curve is chop 1 at **43**, chop 2 at **46**, and chop 3 at **58**, while all three have the same reported completion-state bank-plus-standing-wood value of **25**. A scalar chop-sum target also loses the difference between chop already present on turn 1 and chop arriving much later.

The game-level selector should rank the frontier with a turn-300 terminal value, for example:

`V300 = current banked score + expected additional fruit score + 4 * expected wood actually dropped by turn 300 - expected raid loss`.

The safe offline-fixed third term is therefore **a fixed continuation policy/value function that estimates wood actually banked from the completion state to turn 300**, not raw `chop * (300 - arrival_turn)`. Its code or lookup table can be fixed offline, but its inputs must be live: roster, tree health/size, distances, capacity, positions, and remaining trees. The raw capacity term would be badly biased because walking is **64%** of commands even in the solver's schedules, and the median schedule still contains **14 harvests** and **6 mines** before the third troll.

This continuation value should also replace a plain count of planted trees. Location and type matter: the page's own example has a lemon bearing in **12 turns** near water versus **32 turns** inland. Two equal tree counts are not equal farms.

## 2. The exact 21-turn gain is an idle-board result; the two main rules should survive, but the full number is not yet established

The opening can be changed by an opponent when it changes a scheduled resource state: harvesting or chopping a wild tree before our planned first harvest (median first harvest turn **9**), or putting a tree on a cell intended for one of our plants (the solver plants in **328 of 400** schedules, median first plant turn **5**). Those events can reduce a planned load, remove a target, or force a route repair.

Two things described as "contested" are not genuine blocking resources under the verified referee mechanics:

- enemy units can share cells with ours, so they cannot block a route or an iron-adjacent tile;
- iron cells have no depleting stock, so enemy mining does not consume our future iron.

Thus Stage 2 does **not** need an adversarial path blocker or an iron-allocation model. It needs live validation of tree fruits, tree existence, and intended plant cells, followed by replanning. Shared harvesting is also not purely zero-sum because the referee can duplicate the last fruit when both players harvest it in the same phase.

The measured causes suggest a large part of the advantage is robust: forcing one-item trips costs **7 turns median** on **43 of 51** ablation seats, and delaying the second troll costs **7 turns** on the **30** seats where orchard 6 bought it late. Those are our own scheduling defects, not opponent assumptions. But Stage 1 does not prove that the full median **21-turn** gap survives live tree changes. Until a contested test exists, call 21 turns the **idle-board potential**, not an expected ladder gain.

Stage 2 should replay the live replanner against at least a mirrored strong opening and recorded/top-bot opening policies on the same panel. Report third-troll delay relative to idle, number of plan repairs, failed/short harvests, and the p25/median/p75 completion turns. This is a Stage 2 gate, not a reason to rerun Stage 1's ablation.

## 3. Ship rules first, but the evidence supports two major rules and one tail heuristic, not three equal causes

The split is broadly right.

1. **Move the starting troll off the shack and train an affordable second troll immediately.** The solver does this on turn 1 on **314 of 400** map-seats; where the old bot buys late, the measured penalty is **7 turns**.
2. **Do not use one-item trips as the default.** Their measured cost is **7 turns median**, mean **9.0**, on **43 of 51** seats. The hand-written rule should be "take the useful load up to capacity" rather than "always fill": a smaller load may still be correct when it clears the next bill sooner.
3. **Protect the next training bill from seed spending.** PICK is before TRAIN and DROP is after TRAIN, so a plant-on-the-way rule must be gated by the known bill. This is a referee-order invariant, not a learned choice.
4. **Use water-aware planting as a fallback heuristic, not as a headline source of the 21 turns.** Forcing next-door cells has median cost **0**, mean **2.1**, and changes **18 of 51** seats, though its worst case is **18 turns** and the 12-versus-32-turn lemon example makes it valuable in selected states.
5. **Revalidate every scripted target before acting.** Tree fruits/existence and plant-cell availability are live; an invalid target triggers a repair. Opponent unit position and opponent mining do not.
6. **Keep exact legality, task order, affordability, carry capacity, and no-op prevention outside any learned selector.** The planner or later learned layer may choose the full roster, target tree, useful load, seed programme, and mining time only among those legal macro-actions.

The ablation is not at odds with rules first. It says the first two rules deserve immediate implementation; it also says the planner still matters because walking is **64%** of commands and tree/routing choices create the long tails even when their median ablation is zero.

## 4. The farm formula is algebraically sound as an expectation bound, but "8 trees per 3 chop" is not a safe operating rule

Under the page's assumptions -- constant independent raid hazard `h`, 12-health mature plum/lemon trees, continuous chopping at total power `P`, and no travel -- the exposure calculation and

`F < sqrt(P / (6h))`

are sound. With `P=3` and `h=0.008`, the bound is about **7.9**, hence the displayed **8**.

The interpretation needs tightening. At `F=8`, the same model gives about **1.02 expected raids**. Under a Poisson reading of that approximation, the chance of at least one raid is about **64%**, not a guarantee that all eight are converted first. The owner must choose a risk budget: expected loss below one, 90% probability of no loss, or maximum expected score lead to different farm sizes.

The bound is also strongly phase-dependent: the page gives about **16** trees for `P=3` before turn 100 (`h=0.0019`) and **8** after turn 100 (`h=0.008`). One fixed ratio discards a factor-of-two change already present in the table. It also omits the measured **64%** walking share, banking trips, tree type/health, fruit value before felling, and the policy-dependent nature of the observed raid sample. Use the corrected observed counts in any charter text: **114 / 1,706 = 6.68%** raided and **1,587** self-felled.

Farm **placement and planned conversion order** should be first-class controls; farm size should emerge from them. Score each candidate planted tree by fruit timing, route cost, expected wood score, planned felling turn, and accumulated turn/distance raid exposure. Keep the 8-per-3 number only as an after-turn-100 sanity check under the page's explicit assumptions.

## 5. Two additional Stage 2 gates are required

First, benchmark quality at the actual compute budget. Stage 1's free variant uses about **1,800 rollouts** and **30 seconds** per map-seat at **64 rollouts/s**. The proposed Python first second buys roughly **60 deterministic plans plus 5 random refinements**, while the full four-variant run takes **78 seconds**. The claimed **30-100x** Rust speedup is a projection until the port is measured. This matters because the offline solver is later than orchard 6 on **22 of 292** same-roster seats, with a worst miss of **20 turns**, attributed to search. Stage 2 needs a budget-versus-quality curve against the pinned offline frontier before integration.

Second, expand the roster frontier beyond a chop-only third-troll sweep. The page's free variants hold the third troll at `(2/3/0/c)`, while the task card reports top openings using full tuples such as `(2/3/1/2)` and `(2/4/1/c)`. Stage 2 should value movement, carry, harvest, and chop together; otherwise the terminal value can prefer the wrong cheap arrival.

## 6. What Stage 2 should build first

Build a deterministic, referee-exact, receding-horizon Rust controller before any learned action lane:

1. generate the full-roster Pareto frontier in the first-turn budget;
2. rank it with the fixed turn-300 continuation value fed by the live state;
3. execute one legal macro-action at a time;
4. in each 50 ms turn, validate the scheduled target and repair only when the state changed;
5. pass the idle budget-quality gate and the contested-tree repair gate above.

This is accepted for implementation work. It is not yet accepted as a ladder-ready claim of a 21-turn gain, a fixed 8-tree farm rule, or a raw neural action policy.