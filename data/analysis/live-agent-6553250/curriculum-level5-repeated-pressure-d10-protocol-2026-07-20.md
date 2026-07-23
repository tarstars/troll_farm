# Curriculum Level 5 bounded repeated-pressure D10 protocol — 2026-07-20

## Decision and hypothesis

D9 established that ordinary three-worker scale is viable when renewable supply precedes the
second funding epoch.  On unopened prospective seeds, the fixed actor reached 95.40% while the
opponent created a crop in 99.95%, trained worker three in 95.70%, and destroyed the player's crop
once in 99.45%.  The one-destruction cap, however, tests initial reaction rather than repeated
recovery.

D10 tests one isolated hypothesis:

> allowing the accepted D9 chopper to destroy at most three successively replanted player crops
> will expose whether the fixed actor represents recurrent recovery, while preserving the proven
> crop-before-scale economy and preventing an unbounded denial policy from becoming a confound.

Three is preregistered because it requires two recoveries beyond D9's first contact, yet remains a
small finite intervention.  It is not tuned from D10 outcomes.

## Frozen opponent

Create a distinct `crop-first-funded-trio-repeated-pressure-180` mode.  It inherits D9's map
distribution, randomized recipes, observations, masks, rewards, ordinary training costs, fresh
funding receipts, talents, cap three, crop-before-scale ordering, three productive roles,
turn-180 minimum, 240-turn timeout, and telemetry.

The only causal change is the standard chopper's player-crop predicate:

1. D9 attacks a tracked player crop while the confirmed destruction count is zero.
2. D10 attacks a tracked player crop while that count is below exactly three.
3. A count increases only after an opponent `CHOP` on the tracked player crop removes the banana
   plant in the exact referee state.  Failed travel or chop attempts do not count.
4. After the third confirmed destruction, the chopper permanently returns to D9's natural-tree
   role.  No fourth destruction is allowed.
5. Replanting, crop-site refresh, success logic, and every opponent economic decision remain
   unchanged.  The opponent receives no item, worker, movement, or score gift.

Thus the intervention changes pressure frequency, not workforce economics, episode duration, or
the player's task.

## Integrity and consumed readiness

Implementation and debugging may use only consumed seeds 0--4,999.  Before fresh execution:

- D10 never trains worker three before `opponent_created_crops > 0`;
- both ordinary training costs and fresh-receipt invariants remain intact;
- the opponent never exceeds three workers or three confirmed player-crop destructions;
- deterministic reset/step agreement, observation/action dimensions, and legal teacher actions
  hold;
- D7, D8, and D9 preserve their original horizons and one-destruction behavior; and
- a consumed teacher bank contains episodes with at least two and at least three confirmed
  destructions, proving that the new path—not just its label—is active.

No gate, seed interval, pressure bound, scheduler rule, checkpoint, or policy may change from
readiness outcomes.

## Fresh controls

Run teacher and random legal exactly once on unopened Level-5 seeds 5,000--5,499 with 100
environments, a 240-turn timeout, and random seed 107.  Teacher must reach:

- >=90% overall and nontrivial success;
- >=85% in every recipe and >=88% in every height;
- >=90% terminal player-crop presence and >=95% renewable player harvest;
- zero illegal selected actions and no success before turn 180;
- first-worker training in >=98% and third-worker training in >=85%;
- fresh funding receipts before 100% of both recorded training events;
- standard-chopper productivity in >=98% and feeder productivity in >=80%;
- exactly three terminal rival workers in every recorded third-worker episode and never more than
  three;
- crop creation before every recorded third-worker event, >=95% rival crop creation, and >=80%
  rival own-crop renewable harvest;
- at least one, two, and three confirmed player-crop destructions in >=95%, >=90%, and >=80% of
  episodes respectively; and
- no episode above exactly three confirmed destructions.

Random legal must remain <=5% overall.  Any control failure stops before actor replay, learning,
prospective seeds, deployment, YT writes, or Arena action.

## Fixed-actor gate

Only if every control passes, replay the unchanged accepted Level-4 checkpoint once on the same
seed bank against the exact D10 teacher artifact.  Require:

- >=85% overall and >=82% nontrivial success;
- >=75% in every recipe and >=78% in every height;
- >=80% terminal player-crop presence and >=90% renewable player harvest;
- no success before turn 180 and paired-teacher median completion delay <=30 turns;
- first-worker training >=98%, third-worker training >=85%, both fresh-receipt rates 100%,
  standard-chopper productivity >=98%, and feeder productivity >=80%;
- crop creation before every third-worker event, rival crop creation >=95%, rival own-crop harvest
  >=80%, and a maximum of three workers; and
- at least one, two, and three confirmed destructions in >=95%, >=85%, and >=70% of episodes, with
  no episode above three.

A pass authorizes one separately frozen prospective confirmation on the reserved unopened interval
2,029,000--2,030,999 without learning.  A control-valid actor failure establishes a bounded
recurrent-recovery learning deficit and authorizes failure analysis plus a separately frozen
clone/PPO protocol.  D10 itself authorizes no checkpoint change, deployment, or Arena submission.

## Conditional compute decision

Controls and fixed-actor replay remain local.  If and only if D10 is control-valid and the actor
fails, benchmark the same frozen one-million-transition PPO workload once locally and once on one
YT RTX 4090 allocation.  Record cold allocation/startup separately from steady-state rollout,
optimization, artifact transfer, total wall time, and effective transitions/s.  Use YT for
multi-million-transition replicas only if the measured end-to-end result or the preregistered
training-budget projection is materially faster; otherwise keep training local.  No benchmark is
authorized merely because D10 exists.

## Pre-implementation anchors

- accepted D9 prospective result:
  `fcaf7ac7dc8ef1bdf96a7956359f1fd5190a46fdda4f7d2d6174700903ff5787`;
- Rust source:
  `73f7659abf7114a5cfe33bddd6825c6518b9192cb6e3b60d0bcc80fda30633fb`;
- Level-5 Python environment:
  `aab7a0303b2cf7f2582dca5c1ed90d9a55997460489c3ce7d0dc70d9eb81c427`;
- PPO/evaluation selector:
  `d1fa432aa2b5271207cd4bdedd8495933374cbf7af2530de1b02ba0225d69901`;
- Level-5 evaluator:
  `b797411f6daa7bfb9bd787f22abe112885651375c4bb01e4b03458fac8e3d37c`;
- focused Level-5 tests:
  `a05f0b4e57db822c493ec6636b76c55379fba411db240ba05c7313c54e032350`;
- release shared library:
  `328f64af58f64c885e25c03e0cf806c55c5079824ac559f6faa36db5448c0f43`;
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- fresh Level-5 interval: `[5000, 5500)`, unopened at freeze; and
- reserved prospective interval: `[2029000, 2031000)`, unopened and inaccessible before a D10
  development pass.
