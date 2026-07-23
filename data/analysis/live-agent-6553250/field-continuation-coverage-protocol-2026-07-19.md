# Full-trajectory field-continuation coverage audit — frozen protocol, 2026-07-19

## Question

Does the fixed eight-model local continuation zoo cover the opening and macro trajectories of the
actual Legend opponents faced by the Phase 21 `b100_e6` candidate?  In particular, is adaptive
Gold a meaningful proxy for the worker-rich catastrophic cohort, or merely a synthetic local
counter that should not dominate policy search?

This is a diagnosis-only model-support audit.  It cannot assign rollout weights, reopen a rejected
farm genome, qualify a candidate, or authorize arena work.

## Immutable cohort and pairing

Use the 160 game IDs in `phase21-candidate-field-census-2026-07-19.json`.  All are consumed arena
diagnosis data for candidate agent `6560269`.

For every game:

1. fetch the immutable result read-only;
2. normalize the official initial map so exact `b100_e6` is local player 0 regardless of arena
   seat;
3. retain the actual arena opponent's effective first command and the census's exact referee-
   confirmed trajectory statistics; and
4. from that identical normalized initial state, play exact formatted `b100_e6` against each fixed
   local model through the corrected terminal/stall rule.

The fixed models are CompactGold, adaptive Gold, GoldElite, MyBot, PrinterBot, SchedBot,
ScriptBoss, and SilverBoss.  Do not add, remove, configure, or weight models after seeing results.

## Compared behavior

### Opening

Normalize MSG, duplicate unit commands, and formatting.  Compare:

- TRAIN presence and exact four-stat specification;
- starter action verb;
- exact starter command including target; and
- full effective command set.

`coarse_opening_supported` means TRAIN presence and starter verb both match for at least one model.
`exact_opening_supported` means exact TRAIN spec and exact starter command both match for at least
one model.

### Macro trajectory

At resolved turns 50, 100, and final, compare the local model's side with the actual arena
opponent on eight referee-level features:

- score;
- banked fruit;
- banked wood;
- workers;
- successful plants;
- harvested fruit amount;
- successful chop actions; and
- dropped item amount.

Also compare terminal turn.  Absolute tolerances are frozen:

| Feature | Turn 50 | Turn 100 | Final |
|---|---:|---:|---:|
| score | 20 | 35 | 60 |
| fruit | 6 | 10 | 15 |
| wood | 5 | 8 | 15 |
| workers | 1 | 1 | 1 |
| successful plants | 4 | 8 | 15 |
| harvested fruit | 8 | 15 | 30 |
| chop actions | 15 | 25 | 50 |
| dropped items | 12 | 20 | 40 |

Terminal-turn tolerance is 40 turns.

A model `macro_covers` a game only if at least 20 of 24 checkpoint comparisons pass, final score,
wood, and workers each pass, and terminal turn passes.  A model `fully_covers` only if it both
macro-covers and matches the coarse opening.

For nearest-model diagnostics, scale every absolute feature error by its frozen tolerance and use
the mean across the 24 checkpoint features plus terminal turn.  This ranking is descriptive and
does not relax binary coverage.

## Frozen zoo-adequacy gate

The current zoo is adequate for future robust policy selection only if all checks pass:

1. some model fully covers at least 70% of all 160 games;
2. some model fully covers at least 70% of catastrophic games (margin <= -100);
3. some model fully covers at least 60% of worker-rich games (actual opponent has at least three
   workers at final);
4. at least 50% of games have exact opening support;
5. every actual opponent represented by at least five games has at least 50% full coverage; and
6. the runner reproduces all 160 initial records, both normalized seats, and all 1,280 model cells
   without panic, invalid horizon, or missing checkpoint.

Failure means the zoo must not be used as a calibrated ambiguity set or candidate acceptance
oracle.  Cluster uncovered games by actual opponent, opening TRAIN/spec, worker count, planting,
chopping, and wood trajectory to nominate at most three coherent missing archetypes.

## Adaptive-Gold relevance diagnostic

Without changing the adequacy gate, label adaptive Gold a material field proxy only if it:

- macro-covers at least 20% of catastrophic games and at least 20% of worker-rich games; and
- is the nearest macro model in at least 15% of each cohort.

If this diagnostic fails, the complete-economy smoke's adaptive-Gold veto remains a valid local
robustness failure but cannot be interpreted as direct field evidence.  If it passes, the next
policy grammar must explicitly survive that sustainable shared-supply counter.

## Stop rule

Write the coverage matrix and missing-archetype nomination, then stop.  No controlled platform
game, fresh seed, continuation reconstruction, candidate source, submission, or resident change
is authorized by this audit.
