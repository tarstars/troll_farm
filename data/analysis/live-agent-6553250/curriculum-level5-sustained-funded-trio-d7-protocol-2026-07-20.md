# Curriculum Level 5 sustained funded-trio D7 protocol — frozen 2026-07-20

## Question

Can the accepted actor keep its requested two-role economy valid through turn 120 while the exact
D6 opponent completes two natural funding epochs and operates three roles?

D6 stopped because the ordinary player-0 task terminates at median turn 64, only about 16 turns
after median worker-three training.  The identical opponent activates strongly in random episodes
that continue to turn 240.  D7 changes only the minimum success/evaluation window; it does not make
worker three cheaper, accelerate the opponent, broaden its roles, repeat player-crop destruction,
or alter actor inputs.

## Frozen sustained task

Use the exact D6 opponent, transactions, talents, role assignment, funding receipts, cap, and
telemetry.  Player 0 retains the randomized requested recipe, teacher, action mask, reward shaping,
crop-loss lifecycle, checkpoint, and 240-turn safety horizon.  Before turn 120, satisfying the
existing terminal milestones does **not** end the episode.  At or after turn 120, success requires
all existing conditions simultaneously:

- the requested player-0 worker is present;
- the tracked player-0 BANANA crop currently exists;
- at least one tracked renewable harvest has occurred; and
- score gain since player-0 training is at least 12.

Once all conditions hold at or after turn 120, the ordinary single success bonus and terminal event
occur.  Before then, no repeated success bonus is awarded.  Timeout remains turn 240.  This is a
sustained-validity bridge, not yet a full 300-turn score-maximization objective.

## Integrity and consumed readiness

Implementation may use only consumed seeds 0--3,499.  Before fresh execution:

- every sustained teacher success turn is >=120 and no ordinary Level-1--5 constructor changes;
- waiting through turn 120 remains deterministic for observations, masks, rewards, and all terminal
  telemetry;
- the exact D6 training/funding/role/cap/destruction invariants still pass;
- random legal remains discriminative on a consumed smoke bank; and
- observation/action dimensions remain 104x11x22 and 13x11x22.

No threshold, opponent rule, checkpoint, seed interval, minimum turn, or success milestone may be
tuned from consumed outcomes.

## Fresh D7 development controls

Run teacher and random legal exactly once on seeds 3,500--3,999 with 100 environments, a 240-turn
horizon, minimum success turn 120, and random seed 89.  Teacher must reach:

- >=90% overall and nontrivial success;
- >=85% in every recipe and >=88% in every height;
- >=90% terminal player-crop presence and >=95% renewable harvest;
- zero illegal selected actions and no success before turn 120;
- first-worker training in >=95% and third-worker training in >=85%;
- fresh funding receipts before 100% of both training events;
- standard-chopper productivity in >=90% and feeder productivity in >=75%;
- exactly three terminal opponent workers in every recorded third-worker training episode and never
  more than three;
- >=70% opponent crop creation, >=50% opponent own-crop renewable harvest, and >=80% confirmed
  player-crop destruction; and
- no episode above one tracked player-crop destruction.

Random legal must remain <=5% overall.  Failure stops before actor replay, learning, prospective
seeds, deployment, YT, or Arena action.

## Fixed-actor gate

If controls pass, replay the unchanged accepted Level-4 checkpoint once on the same bank against
the exact teacher artifact.  It must reach:

- >=80% overall and >=78% nontrivial success;
- >=70% in every recipe and >=75% in every height;
- >=85% terminal player-crop presence and >=90% renewable harvest;
- no success before turn 120 and paired-teacher median completion delay <=30 turns; and
- the same training, funding, two-role productivity, workforce-cap, opponent-crop, harvest, and
  destruction gates as the teacher.

A pass permits one separately frozen prospective confirmation without learning.  A valid teacher
plus actor failure permits failure diagnosis and a separately frozen clone/PPO protocol.  D7 does
not authorize deployment or Arena submission.

## Compute decision

Longer episodes remain a small local control/evaluation workload.  YT is deferred unless actor
failure authorizes learning; then a frozen 100,000-transition local-versus-YT-GPU benchmark decides
the training venue.

## Pre-implementation anchors

- stopped D6 result:
  `a26ecc656d13b563e09a482cbc8c5590c8027caef1a28d00c65aa288da0f05bf`;
- Rust source:
  `b8ea3c32b20701efeaffbb4fde10cc3693756e48038581ff4bf3a73bbb435d70`;
- Level-5 Python environment:
  `f34bd40e3c85dd5857501adf78e376b506dc68319d8c849fce5cbdde26d888f2`;
- PPO/evaluation selector:
  `06cdf9aaf7a3df6fca99cb5ad8d197b6e9d6b5a1ff1024f9ed75108a3099350d`;
- Level-5 evaluator:
  `33dd1578da2714cfb6585de62a303c912b824892545354f6e7fc7d1ef0bd530b`;
- focused Python tests:
  `29eefd80d2e361e1419dcc2a7ca4bda05c60131261fb5703ff580d5806a6c604`;
- release shared library:
  `cc19b5dc81889bc8a4603fe3bcfb57cb69330e1ed954b39516ada5adcbbc772f`; and
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
