# Orchard kinetics action-space review

**Agent:** `chatgpt_2`  
**Date:** 2026-09-04  
**Related live card:** `coordination/tasks/20260904-orchard-kinetics.md`  
**Scope:** supplementary static review and a single-tree micro-instrument; no bot build, no panel, no ladder, no Arena action, and no claim to ownership of `claude_1`'s live read.

## Verdict

The owner's observation is exactly right: the wood-aware optimizer I built could not discover an orchard because **planting was not merely disfavoured; it was outside the state graph**.

The repair is not “add one `PLANT` candidate to the dispatcher.” The optimizer's forecast, admission rule and execution policy must all see the same mutable future forest. If only the emitted commands gain a planting heuristic while the admission forecast still values a fixed, depleting `view.plants`, the controller will make mutually inconsistent decisions: one layer spends a turn and a seed to create wood, while the layer deciding whether the third troll pays pretends that wood can never exist.

The correct next model is a joint, event-driven search in which **planting schedule, orchard state and troll roster are one problem**. The original `chatgpt_1/opening-dp-oracle` is a better base for that work than my fixed-deficit enumerator because its reduced action vocabulary already contains `PLANT` and delayed crops.

## 1. What my optimizer actually searched

The decisive functions in `chatgpt_2/three-troll-optimized-start/optimizer.rs.in` are:

- `opening_resource_curve`: harvests only from trees already present in `view.plants`;
- `opening_assignment`: splits a fixed four-resource training deficit between two workers;
- `opening_standing_wood_points`: values only the plants standing **now**;
- `opening_evaluate_third`: caps the third troll's future by that fixed current forest;
- `opening_optimize_third`: chooses only among seven troll talent tuples.

No transition creates a tree, reserves a planting cell, carries a seed forward in time, or changes a future cooldown. The search can answer:

> Given this fixed forest, which two workers should gather the bill for which third troll?

It cannot answer:

> Should a worker spend a seed and a turn now so that a different amount of wood exists when the third troll arrives?

That omission explains the shape of the result. The optimizer repeatedly chose the weakest useful troll because every larger troll had to repay itself from a forest the model knew was shrinking and had no way to enlarge.

## 2. Keep the units straight: a mature tree is up to four wood, hence 16 score points

Wood is worth four score points **per unit**. A size-four tree yields up to four wood units, so its gross standing potential is **16 score points**, before carry, travel, raid and opportunity costs. The orchard read should report both units:

- standing or bankable **wood units**;
- corresponding **score points** (`4 × wood`).

Calling a mature tree “four points” would introduce a factor-of-four unit error into the planting comparison.

The exact single-tree rules give this table. “Full size” and “first fruit” are end-of-turn offsets from the turn on which `PLANT` is issued. Fell turns are for an untouched mature tree and total chop power 1/2/3/4.

| kind | location | effective cooldown | full size | first fruit | mature health | fell turns 1/2/3/4 | gross mature points |
|---|---:|---:|---:|---:|---:|---:|---:|
| plum / lemon | water | 3 | 9 | 12 | 12 | 12 / 6 / 4 / 3 | 16 |
| plum / lemon | inland | 8 | 24 | 32 | 12 | 12 / 6 / 4 / 3 | 16 |
| apple | water | 2 | 6 | 8 | 20 | 20 / 10 / 7 / 5 | 16 |
| apple | inland | 9 | 27 | 36 | 20 | 20 / 10 / 7 / 5 | 16 |
| banana | water | 4 | 12 | 16 | 6 | 6 / 3 / 2 / 2 | 16 |
| banana | inland | 6 | 18 | 24 | 6 | 6 / 3 / 2 / 2 | 16 |

Two consequences matter.

First, tree growth is asynchronous. Nine turns for a water-side plum to reach size four are wall-clock turns, not nine worker-turns: the planter can do other work while it grows. The search must schedule workers and crops independently rather than add “growth time” directly to the planter's cost.

Second, a pure wood orchard must search **all four species**. Once mature, every species offers the same four wood, but a banana has 6 health, a plum or lemon 12, and an apple 20. A chop-1 third troll needs 6 turns for a mature banana, 12 for plum/lemon and 20 for apple. Banana also does not consume one of the three fruit types in the training bill. Therefore bananas are a natural candidate for the standing wood stock intended for a weak third troll. Water-side apples mature fastest, so they can still win when planted late or when chop power is high. The species mix is a search result, not a constant copied from the owner's illustrative sentence.

## 3. Exact ordering constraints that the macro-actions must preserve

The referee executes:

`MOVE → HARVEST → PLANT → CHOP → PICK → TRAIN → DROP → MINE → tick plants`.

This creates non-negotiable constraints:

1. A seed picked this turn cannot be planted this turn because `PLANT` happens before `PICK`, and a troll emits only one ordinary command.
2. A `PICK` spends inventory before `TRAIN`; it can make an otherwise affordable troll fail. The next training bill must be reserved explicitly.
3. A `DROP` happens after `TRAIN`; cargo delivered this turn cannot fund that turn's training.
4. A new tree cannot be chopped on its planting turn. The set of choppable cells is frozen before `PLANT`.
5. The new tree starts at size 0 and cooldown 0, then grows to size 1 in the same turn's final tick.
6. Same-type simultaneous planting intents on one cell merge into one tree while **every planter spends a seed**; mixed-type intents cancel.
7. Chop damage is preserved through later growth; growth adds only the species' health slope.
8. On death, wood distribution depends on chopper capacity and simultaneous choppers. The referee can duplicate the last wood unit. The search must replay this exactly, but an optimistic bound should not rely on the duplication.

A macro-action called `PLANT(kind, cell)` therefore cannot be treated as one instantaneous abstract choice unless it also carries the exact preceding seed acquisition, travel and phase timing.

## 4. The value of a planting turn

For a candidate tree `j`, a useful comparison is:

`plant_value(j) = expected banked wood score + expected fruit taken before felling
                  - seed shadow price
                  - worker opportunity cost
                  - expected raid loss`.

More explicitly:

`Vplant = survival × 4 × bankable_wood_units
          + fruit_value
          - seed_shadow
          - Σ(best alternative value of each occupied worker-turn)
          - raid_loss`.

Important terms:

- **Bankable**, not merely standing, wood: enough chop time, carry capacity and time to return to the shack must remain.
- **Seed shadow price**, not always one: a plum, lemon or apple can be part of the next troll's bill or a future self-replenishing orchard. Its opportunity value may be much larger than its face score.
- **Alternative worker value**, measured from the current state: the cost of planting is the best legal harvest/chop/mine/drop action displaced on those turns, not a global average.
- **Survival**, with time-varying contest risk: the card's measured raid rate is low before turn 100 and roughly three to five times larger after it. A single mean hazard hides the exact phase in which the orchard is supposed to stand.

The third troll should not be admitted by one forecast and the orchard by another. The terminal comparison is:

`best turn-300 value with {PLANT, TRAIN, ...}
 -
 best turn-300 value with the same actions but without that TRAIN`.

Both sides must be optimized against the same opponent scenarios. Otherwise the “with troll” side can be charged for planting that the “without troll” side was never allowed to choose, or vice versa.

## 5. Minimal event-driven state

A usable search state needs:

- current turn;
- banked resources;
- every troll's talents, position, cargo and current macro-job with completion time;
- shack occupancy and whether training has already fired this turn;
- every relevant tree's cell, type, size, health, fruits and cooldown;
- which candidate planting cells remain free;
- our planned orchard cells, because the platform does not transmit planter ownership later;
- opponent scenario or time-dependent raid state;
- accumulated banked score.

Branch only when something can change:

- a worker becomes free;
- a seed is available at the shack;
- a tree grows, bears fruit or reaches the planned felling threshold;
- a delivery makes a training bill affordable;
- an opponent changes a target tree or occupies an intended planting cell;
- a planned tree is raided.

Every macro transition must still compile to ordinary commands and replay through `sim/engine.py` or the maintained Rust engine. Event-driven means fewer decision points, not approximate physics.

## 6. Search objective: retain a frontier before choosing one scalar

For the no-build read, preserve non-dominated states at turns 100, 150, 200, 250 and 300 with at least:

- roster and each troll's arrival turn;
- banked score;
- bank and cargo by item;
- standing wood units by tree and cell;
- bankable wood by the horizon;
- worker positions;
- trees planted, survived, harvested and felled;
- planting worker-turns and displaced wood;
- raid losses.

A state is not dominated merely because it has the same number of trees. A water-side banana ready for a chop-1 troll and an inland apple are not equivalent. Cell, type, health and timing belong in the structural key.

The read can then answer the owner's question without prematurely inventing a universal weight: does any orchard frontier make the third-troll branch beat the no-third branch after all costs?

## 7. Reuse the right search engine

Do **not** extend `opening_assignment` into another larger Cartesian product. It assumes fixed deficits, fixed sources and additive per-worker resource curves. Planting violates all three:

- spending a fruit can create a renewable future source;
- the source appears only after a delay;
- one worker's planting changes the jobs available to every worker;
- tree survival and felling order couple the workers;
- roster choice changes the value of every tree.

The original `chatgpt_1/opening-dp-oracle` already has the correct architecture:

- asynchronous workers;
- event jumps;
- `PLANT` as a transition;
- future crop readiness in the structural state;
- a legal incumbent, admissible bound and dominance pruning;
- an exact certificate or a bounded gap.

The cheapest valid next implementation after the current read is therefore a **real-map fixed-roster adapter** for that engine:

1. Candidate cells are the exact reachable empty cells near the shack, tagged water-side/inland and distance.
2. Fix one third-troll tuple and allow the action set to include seed acquisition, planting, maintaining, felling and training.
3. Replay every selected sequence through the exact engine.
4. Compare against the same search with `PLANT` disabled and against the champion's realized 9.8-tree baseline.
5. Only then add the full roster frontier and the Rust anytime budget.

## 8. Required regression cases before any bot build

1. **Plant-now witness:** no useful standing tree, one seed, one water-side cell, enough horizon. The search must find a profitable planting sequence.
2. **Too-late negative control:** same state with too little time to grow, fell and bank. It must decline.
3. **Species frontier:** with a mature orchard and chop power 1, banana must not be pruned behind apple; with late planting and high chop, water-side apple must remain available.
4. **Bill reservation:** picking a seed that makes `TRAIN` fail must be represented as a real delay, not free planting.
5. **Phase order:** a picked seed cannot plant in the same turn, a dropped resource cannot train in the same turn, and a new tree cannot be chopped in the same turn.
6. **Cell conflict:** mixed species on one cell cancel; same species merge and spend every seed.
7. **Damage preservation:** pre-chopped trees grow by adding health slope rather than healing to full health.
8. **Opponent flip:** a raid scenario must be able to reverse a plan that wins against an idle opponent.
9. **Replay certificate:** every complete schedule reproduces its train turn, final inventories, score and tree states in the exact engine.
10. **Mechanics-valid control:** the control must itself clear the smoke bar. The previous no-optimizer control's 15/24 result is not an admissible control for value claims.

## Straight answer

The third-troll optimizer failed to plant because it was built as a roster-and-bill optimizer over a fixed forest. Adding a local planting heuristic would not fix the model. The orchard and the troll must be co-optimized in one state graph.

The strongest immediate design prediction is also testable: **for a weak third troll whose purpose is wood, mature bananas are structurally attractive because they yield the same four wood as every other mature tree, require the least chopping, and do not consume a plum/lemon/apple training resource.** A valid search must be allowed to discover that—or refute it through seed availability, travel, timing and raid risk—rather than hard-code an apple/plum/lemon orchard.
