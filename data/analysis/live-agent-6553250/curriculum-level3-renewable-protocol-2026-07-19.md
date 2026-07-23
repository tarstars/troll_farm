# Curriculum Level 3 renewable two-troll protocol — frozen 2026-07-19

## Question and boundary

Can the accepted compact spatial actor transfer from funding a worker to operating a coordinated
two-troll renewable economy?

The requested worker remains fixed at standard chopper `(2,2,0,2)` and TRAIN remains automatic.
Once trained, the shared actor makes one sequential decision for the starter producer and one for
the chopper; both stored commands execute simultaneously on the exact referee turn.  The opponent
waits.  Recipe selection, third-worker funding, opponent interaction, and terminal score
differential remain later curriculum levels.  A pass cannot change the resident or authorize an
Arena submission.

Success requires all four conditions by referee turn 240:

1. the chopper is trained;
2. a BANANA crop is planted on the deterministic designated home-area cell;
3. BANANA is later harvested from that exact created crop; and
4. banked score is at least 12 points above the immediate post-training score.

Development seeds 0--499 are consumed.  Their teacher is 500/500 with median training turn 18,
median completion turn 47, and median score gain 16; random legal is 0/500.  These observations
only establish feasibility and do not count as prospective evidence.

## Environment preflight

Before generating learning labels:

- Rust and Python must agree on observation/action shapes and terminal metadata;
- identical batches must be byte-deterministic;
- teacher actions must be legal for at least 1,000 sampled sequential decisions;
- on exactly seeds 2,009,000--2,010,999, the teacher must solve at least 98% overall, 97% of
  nonzero-initial-deficit episodes, and 95% in every height bucket;
- the teacher must create and later harvest its tracked crop in at least 98% of episodes; and
- a random-legal control with RNG seed 71 is generated and hashed on the same interval.

Failure stops before cloning.  The objective, target worker, sequential action semantics, maximum
turns, and all thresholds are immutable after the exact preflight begins.

## Behavior-clone discovery

- initialize from the accepted seed-67 Level-2 confirmation checkpoint;
- model/shuffle seed 71;
- online teacher stream begins at 6,000,000;
- 600,000 decisions, 100 environments, ten decisions per 1,000-row chunk;
- two shuffled epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0, 14 Torch threads;
- deterministic evaluation on the consumed preflight interval.

The clone must achieve at least 75% overall, 70% on nonzero-initial-deficit episodes, 65% in every
height bucket, 80% created-crop rate, 70% renewable-harvest rate, and paired teacher median delay
no greater than 35 referee turns.  Failure closes this clone schedule and PPO does not start.

## PPO discovery

Conditional on clone success:

- initialize from the exact clone checkpoint;
- training stream begins at 6,100,000;
- 100 environments x 100 decision rollouts;
- Stage A at 1,000,000 decisions and final at 4,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale 0.01,
  gradient norm 0.5, target KL 0.03;
- constant online teacher auxiliary coefficient 0.10;
- exact prospective evaluation bank 2,011,000--2,012,999;
- teacher and random-legal controls for that interval are generated and hashed before the first
  learned evaluation; random RNG seed 71.

Stage A requires 65% overall, 60% nontrivial, 55% height floor, 70% crop creation, 60% renewable
harvest, and teacher median delay no greater than 45 turns.  Failure stops.

The final discovery gate requires 90% overall, 85% nontrivial, 80% height floor, 92% crop creation,
90% renewable harvest, at least 50 percentage points over random legal, and teacher median delay
no greater than 30 turns.  The exact action audit must choose the applicable productive milestone
or work action in at least 60% of farmer and chopper opportunities separately and emit at most
20,000 unjustified selected-unit waits across 2,000 episodes.  Waiting on the tracked unripe crop
is explicitly justified and excluded.

## Confirmation and promotion

A full discovery pass authorizes exactly one independent confirmation with model seed 79,
disjoint clone/PPO streams, and a new 2,000-seed exact bank frozen before execution.  Confirmation
requires 85% overall, 80% nontrivial, 70% height floor, 88% crop creation, 85% renewable harvest,
and the same action-collapse limits.  Level 3 is accepted only if discovery and confirmation pass.

Any failure receives a written role/milestone/difficulty diagnosis before a new hypothesis is
selected.  No Level-3 checkpoint is a live bot.
