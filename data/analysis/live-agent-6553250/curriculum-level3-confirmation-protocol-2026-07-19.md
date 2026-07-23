# Curriculum Level 3 independent confirmation protocol — frozen 2026-07-19

## Purpose and immutable boundary

Test whether the accepted discovery result reproduces under a new model/shuffle seed, disjoint
online learning streams, and a new exact evaluation bank.  The environment, standard chopper
target `(2,2,0,2)`, automatic TRAIN transition, 240-turn cap, observation/action representation,
teacher, reward, optimizer schedules, and corrected legal-only auxiliary-label rule are unchanged.
No parameter may be selected from confirmation outcomes.

This protocol is frozen before generating either confirmation control and before consuming any
confirmation learning label.  A pass accepts only Curriculum Level 3.  It does not produce a live
bot or authorize a submission.

## Frozen controls and exact bank

- exact evaluation interval: seeds 2,013,000--2,014,999 (2,000 episodes);
- deterministic teacher control on the complete interval;
- random-legal control with RNG seed 79 on the same interval;
- 100 vector environments and 240 referee turns;
- both controls are written and hashed before clone evaluation or training.

The teacher must achieve at least 98% overall, 97% nontrivial, 95% in every height bucket, 98%
tracked-crop creation, and 98% renewable harvest.  Failure invalidates the bank before learning.
Random legal remains a discriminative diagnostic and has no minimum or maximum required outcome.

## Independent transfer clone

- initialize from the accepted seed-67 Level-2 confirmation checkpoint;
- model/shuffle seed 79;
- online teacher stream begins at 6,400,000;
- exactly 600,000 decisions with 100 environments and ten decisions per 1,000-row chunk;
- two shuffled epochs per chunk, minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0, 14 Torch threads;
- deterministic evaluation on the frozen confirmation interval.

The clone gate is unchanged from discovery: at least 75% overall, 70% nontrivial, 65% in every
height bucket, 80% tracked-crop creation, 70% renewable harvest, and paired teacher median delay
no greater than 35 turns.  Failure stops before PPO.

## Independent PPO

- initialize from the exact independent clone checkpoint;
- model seed 79 and training stream beginning at 6,500,000;
- 100 environments x 100 decision rollouts;
- Stage A at 1,000,000 decisions and final at 4,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale 0.01,
  gradient norm 0.5, target KL 0.03;
- constant online teacher auxiliary coefficient 0.10;
- undefined illegal auxiliary teacher targets are skipped and counted; all legal labels remain;
- deterministic Stage-A and final evaluations use the frozen confirmation bank.

Stage A retains the discovery safety stop: 65% overall, 60% nontrivial, 55% height floor, 70% crop
creation, 60% renewable harvest, and teacher median delay no greater than 45 turns.

The final confirmation gate, frozen by the base protocol, requires at least 85% overall, 80%
nontrivial, 70% in every height bucket, 88% tracked-crop creation, 85% renewable harvest, and
paired teacher median delay no greater than 30 turns.

The separately executed strict audit must also obtain at least 60% exact productive-command choice
for the farmer and chopper independently and at most 20,000 combined unjustified selected-unit
waits.  Productive opportunities, exact spatial matching, and the tracked-unripe-crop wait exemption
are identical to discovery.

## Decision rule

All controls, clone artifacts, PPO checkpoints, evaluations, summaries, and the strict audit are
hashed.  If every gate passes, discovery and confirmation jointly accept Level 3 and the next
eligible work is a new curriculum-level design.  If any gate fails, write a milestone/role/height
diagnosis before selecting a new hypothesis.  Confirmation results may not be used to rerun seed
79 with altered hyperparameters or a replacement bank.

The unused 6,300,000 stream is deliberately left as a buffer after the corrected discovery stream;
it is not a hidden development run.
