# Curriculum Level 5 sustained funded-trio D8 protocol — 2026-07-20

## Decision and hypothesis

D7 stopped because the exact paid three-worker opponent created a crop in 68.60% of fresh
turn-120 teacher episodes, below its frozen 70% floor, even though worker-three training, feeder
productivity, own-crop harvest, and destruction passed.  D8 tests one narrow hypothesis:

> keeping the identical interaction alive through turn 180 is sufficient for a robustly active
> three-role opponent economy, after which the unchanged accepted Level-4 actor can be evaluated
> without modifying the opponent or learning target.

No price, inventory, map, talent, role, command priority, reward, player observation, action mask,
terminal milestone, or timeout changes.  D8 changes only the minimum success turn from 120 to 180.

## Frozen D8 task

Create a separate `funded-trio-sustained-180` mode.  It uses the exact D6/D7 opponent:

- the starter must bank a fresh external cost item before each ordinary training transaction;
- worker two is the `(2,2,0,2)` standard chopper bought at the one-worker price;
- worker three is the `(1,1,1,0)` feeder bought at the two-worker price after a new funding epoch;
- the opponent is capped at exactly three workers;
- after scale-up the starter is the regenerative planter, worker two remains the bounded chopper,
  and worker three forages natural resources; and
- at most one tracked player crop may be destroyed.

Player 0 retains its randomized requested recipe, accepted teacher, action mask, shaping,
crop-loss lifecycle, and 240-turn safety horizon.  Before turn 180, satisfying the existing
terminal milestones does not terminate or repeat the success reward.  At or after turn 180,
success still requires all four existing conditions simultaneously:

- the requested player worker is present;
- the tracked player BANANA crop currently exists;
- at least one tracked renewable player harvest has occurred; and
- score gain since player training is at least 12.

The mode must be distinct from D7 so the already tested turn-120 behavior cannot silently change.

## Integrity and consumed readiness

Implementation and debugging may use only consumed seeds 0--3,999.  Before fresh execution:

- no D8 teacher success may occur before turn 180;
- the D7 mode still terminates no earlier than turn 120;
- all earlier Level-1--5 modes preserve their minimum success turns and dimensions;
- D6 funding, roles, worker cap, and destruction invariants remain exact;
- observation/action dimensions remain 104x11x22 and 13x11x22;
- deterministic reset/step agreement passes; and
- teacher and random legal remain discriminative on a consumed smoke bank.

No gate, seed interval, minimum turn, actor, checkpoint, or opponent behavior may be changed from
consumed readiness outcomes.

## Fresh D8 development controls

Run teacher and random legal exactly once on seeds 4,000--4,499 with 100 environments, a 240-turn
horizon, and random seed 97.  The exact seed interval is unopened at protocol freeze.  Teacher
must reach:

- >=90% overall and nontrivial success;
- >=85% in every recipe and >=88% in every height;
- >=90% terminal player-crop presence and >=95% renewable player harvest;
- zero illegal selected actions and no success before turn 180;
- first-worker training in >=98% and third-worker training in >=92%;
- fresh funding receipts before 100% of both training events;
- standard-chopper productivity in >=98% and feeder productivity in >=88%;
- exactly three terminal opponent workers in every recorded third-worker training episode and
  never more than three;
- >=80% opponent crop creation, >=65% opponent own-crop renewable harvest, and >=95% confirmed
  player-crop destruction; and
- no episode above one tracked player-crop destruction.

The 80%/65% crop-loop floors require material improvement over D7's 68.60%/50.60%, while remaining
inside the 81.80%/73.40% long-episode activation already observed in D7 random legal.  The 92%/88%
third-worker floors similarly sit between D7 teacher and timeout-length activation.  They are
fixed from prior consumed evidence, not D8 outcomes.

Random legal must remain <=5% overall.  Any failure stops before actor replay, learning,
prospective seeds, deployment, YT, or Arena action.

## Fixed-actor gate

Only if every control passes, replay the unchanged accepted Level-4 checkpoint once on the same
seeds against the exact teacher artifact.  It must reach:

- >=75% overall and >=72% nontrivial success;
- >=60% in every recipe and >=65% in every height;
- >=85% terminal player-crop presence and >=90% renewable player harvest;
- no success before turn 180 and paired-teacher median completion delay <=30 turns; and
- every D8 opponent training, funding, productivity, cap, crop, harvest, and destruction floor
  required of the teacher.

A pass authorizes one separately frozen prospective confirmation without learning.  A
control-valid teacher plus actor failure establishes a real sustained-interaction learning deficit
and authorizes diagnosis plus a separately frozen clone/PPO protocol.  D8 itself authorizes no
deployment or Arena submission.

## Compute decision

D8 controls and fixed-actor evaluation remain local because they are small and complete in
seconds.  If actor failure authorizes learning, first run the already chosen frozen
100,000-transition end-to-end benchmark locally and on one YT RTX 4090 allocation.  Use YT only if
the measured wall-clock advantage, including startup and artifact transfer, is material for the
planned multi-million-transition run.  No YT work is authorized by control failure.

## Pre-implementation anchors

- stopped D7 result:
  `ea970d188527cdf0ec3237dbd683a69c62840f5c851c7f8ad12f53a77f027511`;
- D7 teacher artifact:
  `4aa1c41e136f21c4ba6f3a9e56eb8afaa0953526fdf8def77ff25024610a8538`;
- D7 random-legal artifact:
  `c5f36cfa3bfc7a4e26f7a6ff7408c4df312c104e541189e8d2205a35a935a10e`;
- Rust source:
  `32b59aadfc295c3ac5d531f42753bac21ac4c59aff9addc7985cb913253caaeb`;
- Level-5 Python environment:
  `e522c1c9ecfba304ac2d2a730b39370d35e5ab2a30d653085a7be81302cb346b`;
- PPO/evaluation selector:
  `c6f76600af9d8b843baee042106cf6315508059bd1352c0394356e1f6483e251`;
- Level-5 evaluator:
  `525857a65eba207bbc4100e9819cb02fb318cfdf97ab085aa4451e686ef1727c`;
- focused Level-5 tests:
  `9a6dc971db76c8a132fbb314278b35b676bcd631a198cee0a6b46944548d5ec4`;
- release shared library:
  `570cfe1e0f114446e00c94c9a95e68f4eb90d09636e9367b9df66587432d5bcf`; and
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
