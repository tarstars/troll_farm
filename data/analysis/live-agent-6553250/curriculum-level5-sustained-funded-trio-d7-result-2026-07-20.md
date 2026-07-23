# Curriculum Level 5 sustained funded-trio D7 result — 2026-07-20

## Verdict

**Stop D7 at fresh controls.**  On fresh seeds 3,500--3,999 the turn-120 teacher and random legal
solve 500/500 and 0/500.  The paid third worker trains in 85.80%, its feeder role is productive in
80.00%, and the rival harvests its own renewable crop in 50.60%.  However, rival crop creation is
**68.60% (343/500)** against the frozen 70% (350/500) activation floor.  Per protocol, the accepted
actor, learning, prospective seeds, deployment, YT, and Arena remain closed.

This is a seven-episode shortfall, but the threshold was fixed before fresh execution and is not
relaxed.  D7 therefore does not establish that the accepted actor handles a sustained three-worker
opponent.

## Frozen control decision

| Measure | Teacher result | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **100% / 100%** | >=90% / >=90% | pass |
| Worst recipe / height | **100% / 100%** | >=85% / >=88% | pass |
| Player crop / renewable harvest | **100% / 100%** | >=90% / >=95% | pass |
| Illegal selected actions | **0** | 0 | pass |
| Success before turn 120 | **0** | 0 | pass |
| Median success turn | **120** | >=120 | pass |
| First-worker training | **100%** | >=95% | pass |
| Third-worker training | **85.80%** | >=85% | pass |
| Fresh receipt before both training events | **100%** | 100% | pass |
| Standard-chopper productivity | **99.80%** | >=90% | pass |
| Feeder productivity | **80.00%** | >=75% | pass |
| Maximum opponent workers | **3** | <=3 | pass |
| Opponent crop creation | **68.60%** | >=70% | **fail** |
| Opponent own-crop harvest | **50.60%** | >=50% | pass |
| Confirmed player-crop destruction | **99.60%** | >=80% | pass |
| Destruction above one | **0** | 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The teacher is completely functional at the player objective: every recipe and height succeeds,
every episode retains the tracked crop and renewable harvest, and all successes occur exactly at
the fixed minimum turn.  Random legal remains fully discriminative.  The only invalid control is
insufficiently robust activation of the rival planter after its second funding epoch.

## What turn 120 changed

| Opponent mechanism | D6 early-terminal teacher | D7 turn-120 teacher | Change |
|---|---:|---:|---:|
| Third-worker training | 55.20% | **85.80%** | +30.60 pp |
| Feeder productivity | 43.40% | **80.00%** | +36.60 pp |
| Rival crop creation | 32.80% | **68.60%** | +35.80 pp |
| Rival own-crop harvest | 13.40% | **50.60%** | +37.20 pp |
| Player-crop destruction | 92.40% | **99.60%** | +7.20 pp |

Holding the opponent fixed while delaying success from median turn 64 to turn 120 removes most of
the D6 censoring.  Worker three now arrives at median turn 54 and is productively used in four of
five episodes.  Crop creation still trails that transaction because the starter must complete
funding, planting, and survival-to-creation after the third worker appears.  Turn 120 is therefore
a useful bridge, but not a control-valid sustained crop economy.

## Analysis at different abstraction levels

### Transaction and workforce

Both ordinary training transactions remain genuinely funded: every recorded training event has a
fresh external receipt, the opponent never exceeds three workers, and the new third worker acts
productively in 400/500 episodes.  Affordability is no longer the limiting mechanism.

### Scheduling

The remaining lag is downstream of training.  The starter alternates between the second funding
epoch and regenerative planting while the other workers keep their chopper and feeder roles.
Sixty additional turns nearly double crop and harvest activation, showing that role sequencing and
available production time—not a cheaper training price—control the observed rate.

### Curriculum

A fixed minimum turn is the correct axis: it changes observation time without altering opponent
economics or actor inputs.  The preregistered next bridge is turn 180 under the same 240-turn safety
horizon.  That will test whether the remaining planter activation is merely late or intrinsically
fragile.

### Learning and compute

No accepted-actor result exists at D7, so there is still no learning deficit and no reason to spend
YT capacity.  These controls run locally in seconds.  If a control-valid sustained task later makes
the actor fail, a frozen 100,000-transition local-versus-YT-GPU benchmark will decide the training
venue before clone/PPO.

### Goal and transfer

D7 creates no submission candidate and no Arena evidence.  It does establish that a naturally
funded third-worker economy becomes materially active when the objective is held open, narrowing
the next question to a longer sustained interaction rather than workforce-price tuning.

## Next hypothesis

Retain the exact D6/D7 opponent, transactions, roles, telemetry, milestones, and 240-turn timeout,
but require success at or after turn 180.  Preregister a new control bank before implementation.
Only a passing teacher/random control may expose the unchanged accepted Level-4 actor.

## Reproducibility anchors

- D7 protocol:
  `582c5069d07b6910ab968deb4ac2f0d0b516d88af10822c03c035620268ea381`;
- readiness record:
  `bf5696435b12b8f52420a01b6101bc1facd4bb91d3d12abbe55b103b942b0c87`;
- teacher artifact:
  `4aa1c41e136f21c4ba6f3a9e56eb8afaa0953526fdf8def77ff25024610a8538`;
- random-legal artifact:
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
  `9a6dc971db76c8a132fbb314278b35b676bcd631a198cee0a6b46944548d5ec4`; and
- accepted checkpoint, deliberately not evaluated:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
