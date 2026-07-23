# Curriculum Level 4 randomized-recipe renewable protocol — frozen 2026-07-19

## Question and isolation boundary

Can one shared spatial policy condition the complete two-role renewable economy on the requested
first-worker recipe?  Level 4 composes the two accepted abstractions: Level 2's deterministic
eight-recipe assignment and Level 3's sequential control of the starter plus trained worker through
crop creation, renewable harvest, and post-training score gain.

The opponent continues to wait, TRAIN remains automatic, and only the first worker is requested.
No opponent policy, recipe selection, third worker, combat, crop theft, live replay, or Arena result
is introduced.  A pass establishes compositional recipe conditioning; it does not establish live
transfer or authorize a submission.

This protocol, seed bank, streams, schedules, and gates are frozen before the Level-4 environment
is implemented or any Level-4 control is generated.  Implementation failures may be repaired, but
outcomes may not be used to change this discovery run.

## Environment contract

- exact Bronze map generator and fast referee used by Levels 1--3;
- recipe assignment is the unchanged Level-2 SplitMix64 mapping and catalog:
  `(1,1,1,1)`, `(1,2,1,1)`, `(2,2,1,1)`, `(2,2,2,1)`, `(1,3,0,1)`,
  `(1,2,0,2)`, `(2,2,0,2)`, `(2,3,1,2)`;
- observation and 13-plane spatial action vocabulary remain exactly 104 x 11 x 22 and
  13 x 11 x 22; target channels 86--89 carry the episode's requested recipe;
- before training, the policy controls the starter and the environment submits the episode's
  recipe every referee turn;
- after training, one referee turn is two sequential decisions ordered by stable own-unit ID;
- the starter retains Level 3's farmer role; the requested worker retains the chopper/score role;
- tracked crop type remains BANANA and required post-training score gain remains 12;
- success requires the exact requested worker, tracked crop creation, at least one harvest from
  that crop, and score gain at least 12 within 240 referee turns;
- reward, legal masks, teacher logic, crop-cell selection, role ordering, and timeout accounting
  are Level 3's unchanged rules with the target constant replaced by the episode recipe;
- terminal metadata adds recipe ID and exact worker specification.

Level 3's fixed-target ABI and outputs must remain bit-for-bit behaviorally compatible on a frozen
debug trace.  Rust/Python agreement, deterministic batches, legal teacher commands, all recipe
IDs, exact terminal recipe metadata, and fixed-Level-3 regression are mandatory implementation
tests.

## Frozen discovery controls

- exact evaluation interval: seeds 2,015,000--2,016,999 (2,000 episodes);
- 100 vector environments, 240 referee turns;
- deterministic teacher on the complete interval;
- random legal with RNG seed 83 on the complete interval;
- both controls are written and hashed before clone training.

The bank is valid only if the teacher obtains at least 98% overall, 97% on nonzero-total-deficit
episodes, 95% in every recipe family, 95% in every height bucket, 98% crop creation, and 98%
renewable harvest.  Random legal is a discriminative diagnostic and has no outcome threshold.

## Transfer clone

- initialize from the accepted independent Level-3 PPO checkpoint with SHA-256
  `a0a0f4bd590175d45be4ec63a8394a47cbe475187d942906d4e01038a167b0df`;
- model/shuffle seed 83;
- online teacher stream begins at 6,600,000;
- exactly 800,000 decisions with 100 environments and ten decisions per 1,000-row chunk;
- two shuffled epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0, 14 Torch threads;
- one deterministic evaluation on the frozen discovery bank.

The clone must reach 70% overall, 65% nontrivial, 55% in every recipe, 60% in every height,
75% crop creation, 65% renewable harvest, and paired teacher median delay at most 45 turns.
Failure stops before PPO and receives a recipe x milestone diagnosis.

## PPO discovery

- initialize from the exact passing Level-4 clone;
- model seed 83 and environment stream beginning at 6,700,000;
- 100 environments x 100-decision rollouts;
- Stage A at 1,000,000 decisions and final at 4,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale 0.01,
  gradient norm 0.5, target KL 0.03;
- constant online teacher auxiliary coefficient 0.10;
- auxiliary teacher labels that are illegal in learner-diverged states are skipped and counted;
  all legal labels remain;
- deterministic Stage-A and final evaluations use the frozen discovery bank.

Stage A requires 60% overall, 55% nontrivial, 45% recipe floor, 50% height floor, 65% crop
creation, 55% renewable harvest, and paired teacher median delay at most 55 turns.  Failure stops
the unchanged run.

The final discovery gate requires 88% overall, 83% nontrivial, 75% recipe floor, 75% height floor,
90% crop creation, 87% renewable harvest, at least 50 percentage points over random legal, and
paired teacher median delay at most 35 turns.

## Frozen action-quality audit

After a functional pass, replay the final deterministic actor on the exact bank.  A productive
choice is exact equality with the teacher's legal spatial command at a post-training opportunity;
waiting on the tracked unripe crop is the only exemption.  Require:

- at least 55% exact productive-command choice for starter farmer and trained worker separately;
- at least 35% exact productive-command choice for each role within every nonempty recipe family;
- at most 30,000 combined unjustified selected-unit waits.

This audit guards against a high aggregate score produced by role or recipe collapse.

## Decision and confirmation boundary

A full discovery pass authorizes one independent confirmation only.  Confirmation must use model
seed 89, disjoint clone/PPO streams beginning at 6,800,000 and 6,900,000, and exact seeds
2,017,000--2,018,999 frozen before confirmation begins.  Its lower final floors are 83% overall,
78% nontrivial, 68% recipe, 68% height, 86% crop creation, 82% renewable harvest, 40 percentage
points over random legal, delay at most 40 turns, per-role exact choice 50%, per-recipe/role exact
choice 30%, and at most 35,000 unjustified waits.

Only discovery plus confirmation accepts Level 4.  Any failed gate is analyzed by recipe, map
height, initial deficit, training milestone, crop milestone, harvest milestone, role, and action
plane before one new hypothesis is selected.
