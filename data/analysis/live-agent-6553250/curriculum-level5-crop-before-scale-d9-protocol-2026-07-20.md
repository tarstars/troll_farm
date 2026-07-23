# Curriculum Level 5 crop-before-scale D9 protocol — 2026-07-20

## Decision and hypothesis

D6 through D8 held the same opponent open for progressively longer objectives.  By turn 180,
worker three trains in 92.60%, yet crop creation remains 76.60% overall and 82.72% conditional on
training.  Code-path analysis identifies a serial scheduler conflict: immediately after worker two
is bought, the starter abandons the accepted D5 planting loop to fund worker three; after training,
the starter and new feeder compete for remaining natural fruit.

D9 tests one isolated hypothesis:

> preserving the two-worker planter/chopper economy until one rival crop exists, and only then
> opening the ordinary second funding epoch, will make naturally paid three-worker scale a robust
> interaction rather than a race between workforce purchase and seed establishment.

This is supply-before-scale ordering.  It is not a worker gift, price reduction, inventory gift,
talent change, or extra resource.

## Frozen opponent

Create a distinct `crop-first-funded-trio-sustained-180` mode.  It inherits D8's turn-180 player
task, 240-turn timeout, map distribution, observations, masks, rewards, milestones, and terminal
telemetry.  Opponent behavior is frozen as follows:

1. With one worker, execute the exact D5/D8 first funding epoch and buy `(2,2,0,2)` at the ordinary
   one-worker price after a fresh external cost receipt.
2. With exactly two workers and no currently tracked rival crop, execute the accepted D5 roles:
   the starter is the regenerative planter and worker two is the standard chopper.  Training worker
   three is forbidden in this state.
3. Once a tracked rival crop exists, begin the exact D6/D8 second funding epoch.  The starter uses
   the unchanged natural-resource/mining funder; the standard chopper remains productive.  Buy
   `(1,1,1,0)` at the ordinary two-worker price only after the existing fresh-receipt condition.
4. With three workers, restore the exact D6/D8 roles: starter regenerative planter, worker two
   standard chopper, worker three natural feeder.
5. Retain the cap of three and at most one tracked player-crop destruction.

If the pre-scale crop is destroyed during funding, the controller does not receive a gift or
special recovery action; after worker three arrives the existing regenerative planter handles the
ordinary loss.  The only code-level causal change is the two-worker predicate that delays the
second funding state until a crop exists.

## Integrity and consumed readiness

Implementation and debugging may use only consumed seeds 0--4,499.  Before fresh execution:

- D9 never trains worker three before `opponent_created_crops > 0`;
- both ordinary training costs, fresh-receipt assertions, talents, roles, cap, and destruction
  invariants pass;
- D8 remains fixed at turn 180 and D7 at turn 120;
- D9 cannot succeed before turn 180;
- deterministic reset/step agreement and dimensions remain unchanged; and
- teacher/random remain discriminative on consumed smoke banks.

No gate, seed interval, scheduler rule, checkpoint, or policy may change from readiness outcomes.

## Fresh D9 controls

Run teacher and random legal exactly once on unopened seeds 4,500--4,999 with 100 environments, a
240-turn timeout, and random seed 101.  Teacher must reach:

- >=90% overall and nontrivial success;
- >=85% in every recipe and >=88% in every height;
- >=90% terminal player-crop presence and >=95% renewable player harvest;
- zero illegal selected actions and no success before turn 180;
- first-worker training in >=98% and third-worker training in >=85%;
- fresh funding receipts before 100% of both training events;
- standard-chopper productivity in >=98% and feeder productivity in >=80%;
- exactly three terminal rival workers in every recorded third-worker training episode and never
  more than three;
- >=95% rival crop creation, >=80% rival own-crop renewable harvest, and >=95% confirmed
  player-crop destruction;
- crop creation before every recorded third-worker training event, enforced by the Rust invariant;
  and
- no episode above one tracked player-crop destruction.

The crop/harvest floors are anchored by the earlier D5 two-worker teacher's 93.80%/79.00% at a
median turn-61 objective.  D9 gives the same roles through turn 180 but then adds a real funding
burden, so 95%/80% requires robust supply without assuming perfection.  The lower 85%/80%
third-worker/feeder floors account prospectively for the new, deliberate planting opportunity cost.

Random legal must remain <=5% overall.  Any control failure stops before actor replay, learning,
prospective seeds, deployment, YT, or Arena action.

## Fixed-actor gate

Only if every control passes, replay the unchanged accepted Level-4 checkpoint once on the same
bank against the exact D9 teacher artifact.  Require:

- >=75% overall and >=72% nontrivial success;
- >=60% in every recipe and >=65% in every height;
- >=85% terminal player-crop presence and >=90% renewable player harvest;
- no success before turn 180 and paired-teacher median completion delay <=30 turns; and
- all D9 training, funding, crop-before-training, productivity, cap, crop, harvest, and destruction
  floors required of the teacher.

A pass authorizes one separately frozen prospective confirmation without learning.  A valid
teacher plus actor failure establishes the first sustained three-worker learning deficit and
authorizes diagnosis plus a separately frozen clone/PPO protocol.  D9 itself authorizes no
deployment or Arena submission.

## Compute decision

Controls and fixed-actor replay remain local.  If and only if a valid D9 teacher plus actor failure
opens learning, benchmark the same frozen 100,000 end-to-end transitions locally and on one YT RTX
4090 allocation.  Use YT for the multi-million-transition run only if measured total wall time,
including launch and artifacts, materially improves.

## Pre-implementation anchors

- stopped D8 result:
  `1862b07d5b33914df01687d575dbc7cf2164e271817fdb86cc1cf433d0471372`;
- Rust source:
  `fbda7052ca1bdf842dbadc32bb0fcf619b89b4cee79d680255e5ecead29946e4`;
- Level-5 Python environment:
  `6791307e5a32a6850be593d12a0c73678a683c99c427ace06a86762ce74989a0`;
- PPO/evaluation selector:
  `4984e20ed6002f4c6f9b87c48e19e53f792f1401e42d4bcbfe16b903aec85a99`;
- Level-5 evaluator:
  `9664da43483b3b0a2cb5585ce92ac7fa02b7ededde2a401efe3604d5f6b8c034`;
- focused Level-5 tests:
  `71d3c4415c58cb6968dcc21a98f95e43d68d7c05e4984e7982c4e44beb34ef34`;
- release shared library:
  `a4ce9d5460afc13fa2e288e7b9cdd15198481daa877db975b2b38fe114facf81`;
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
  and
- fresh seed interval:
  `[4500, 5000)`, unopened at protocol freeze.
