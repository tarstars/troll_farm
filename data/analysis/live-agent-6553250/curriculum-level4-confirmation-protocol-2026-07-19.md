# Curriculum Level 4 independent confirmation protocol — frozen 2026-07-19

## Purpose and independence boundary

Reproduce the seed-83 Level-4 discovery result with an independently initialized learning path.
The question remains exactly the frozen discovery question: can one shared spatial policy
condition the complete two-role renewable economy on any of eight requested first-worker recipes
against a waiting opponent?

This confirmation restarts from the accepted independent Level-3 checkpoint, not from any
Level-4 discovery checkpoint.  Architecture, observation/action ABI, environment, recipe catalog,
role assignment, reward, teacher, optimizer, and schedules are unchanged from the discovery
protocol with SHA-256
`aef6cdd612d57423509f057b5aceaee669af43771b658cb369091b7befaa7418`.
Only the already frozen confirmation seeds, streams, and gates below differ.  No opponent policy,
third worker, recipe selector, combat, crop theft, resident edit, or live submission enters this
experiment.

This file is frozen after discovery passed but before any confirmation control or learning label
is generated.  Implementation defects may be repaired, but confirmation outcomes may not select
a checkpoint, tune a schedule, change a gate, or reuse discovery data.

## Fixed environment and exact bank

- curriculum level 4, 100 vector environments, and 240 referee turns;
- exact evaluation interval 2,017,000--2,018,999 (2,000 episodes);
- unchanged eight-recipe SplitMix64 assignment and Level-4 terminal contract;
- deterministic teacher control on the complete interval;
- random-legal control with RNG seed 89 on the complete interval;
- both controls are written and hashed before clone labels are consumed.

The bank is valid only if the teacher reaches 98% overall, 97% nontrivial, 95% in every recipe,
95% in every height, 98% crop creation, and 98% renewable harvest.  Random legal remains a
discriminative diagnostic without an outcome threshold.

## Independent transfer clone

- initialize from accepted Level-3 checkpoint SHA-256
  `a0a0f4bd590175d45be4ec63a8394a47cbe475187d942906d4e01038a167b0df`;
- model/shuffle seed 89;
- online teacher stream begins at 6,800,000;
- exactly 800,000 decisions, 100 environments, ten decisions per 1,000-row chunk;
- two shuffled epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0, 14 Torch threads;
- one deterministic evaluation on the exact confirmation bank.

Use the unchanged clone safety gate: 70% overall, 65% nontrivial, 55% every recipe, 60% every
height, 75% crop creation, 65% renewable harvest, and paired-teacher median delay at most 45
turns.  Failure stops before PPO and is diagnosed without tuning this confirmation.

## Independent PPO

- initialize from the exact passing seed-89 confirmation clone;
- model seed 89 and environment stream beginning at 6,900,000;
- 100 environments x 100-decision rollouts;
- Stage A at 1,000,000 decisions and final at exactly 4,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale 0.01,
  gradient norm 0.5, target KL 0.03;
- constant online legal-teacher auxiliary coefficient 0.10;
- undefined teacher labels in learner-diverged states are skipped and counted;
- deterministic Stage-A and final evaluations use the exact confirmation bank.

The unchanged Stage-A safety gate requires 60% overall, 55% nontrivial, 45% recipe floor, 50%
height floor, 65% crop creation, 55% renewable harvest, and delay at most 55 turns.  A failure
stops the run.  There is no adaptive checkpoint selection.

The prospective confirmation final gate, frozen in the discovery protocol before Level-4
implementation, requires:

- at least 83% overall and 78% nontrivial success;
- at least 68% success in every recipe and every height bucket;
- at least 86% tracked-crop creation and 82% renewable harvest;
- at least 40 percentage points over random legal;
- paired-teacher median delay at most 40 turns.

## Strict confirmation action audit

After a functional pass, replay the final deterministic actor on the exact bank with the same
productive-opportunity definition and sole unripe-crop wait exemption as discovery.  Require:

- at least 50% exact productive-command choice for farmer and chopper separately;
- at least 30% exact productive-command choice in every nonempty recipe-role cell;
- at most 35,000 combined unjustified selected-unit waits.

## Decision rule

Passing the teacher-bank validity check, clone safety gate, Stage-A safety gate, final functional
gate, and strict action audit accepts Curriculum Level 4 together with the discovery result.
Failure rejects confirmation and triggers a preregistered diagnosis by recipe, height, initial
deficit, training/crop/harvest milestone, role, and action plane before any new experiment.

Acceptance still does not authorize a live submission.  It advances the research program to one
isolated opponent-interaction abstraction while retaining the accepted randomized-recipe,
two-role renewable controller as the fixed base.
