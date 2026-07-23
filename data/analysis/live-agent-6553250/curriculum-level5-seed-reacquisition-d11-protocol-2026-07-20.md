# Curriculum Level 5 seed-reacquisition expert D11 protocol — 2026-07-20

## Decision and hypothesis

D10's exact three-contact opponent is economically valid and recurrently active, but the frozen
teacher succeeds in only 87.00% of fresh episodes.  A post-decision cutoff screen rejects late
pressure as the cause.  Code inspection instead finds an absorbing expert state: when crop,
carried banana, and home banana inventory are empty, the farmer waits at home rather than sourcing
a real replacement seed.  A consumed-screen fallback raises success to 99.40% and three-contact
activation to 96.20%.

D11 tests one isolated hypothesis:

> adding deterministic natural banana reacquisition to the reference expert will establish that
> the unchanged D10 recurrent-pressure task is feasible, after which the fixed actor can provide a
> valid test of post-depletion recovery knowledge.

This is an expert-coverage repair.  It is not an easier opponent, seed gift, reserve gift, reward
change, or actor feature.

## Frozen task and expert change

Create a distinct `crop-first-funded-trio-repeated-pressure-reacquire-180` mode.  For every
externally supplied player action, it must produce the exact same observations, masks, rewards,
opponent commands, referee transitions, objectives, terminal conditions, and telemetry as D10.
It preserves:

- ordinary two-epoch funding, crop-before-scale ordering, talents, and cap three;
- the exact three-confirmed-destruction limit and continuous pursuit behavior;
- turn-180 minimum, 240-turn timeout, recipes, maps, and action vocabulary; and
- all player logic except `teacher_actions` in the exact fallback state below.

Only after the target worker is built, when the active farmer has no crop, no carried item, and no
home banana inventory, the D11 teacher selects the existing deterministic `best_source(BANANA)`.
That source minimizes distance plus regrowth wait over reachable real plants.  At a ready banana
source with free capacity, harvest; otherwise move/wait there.  Once a banana is carried, the
unchanged teacher branch plants it at the existing planned crop site.

No source may be spawned, refilled, moved, or made private.  The fallback may use any real reachable
banana plant already represented in observations, including a rival crop.

## Integrity and consumed readiness

Implementation and debugging may use only consumed Level-5 seeds 0--5,499.  Before fresh execution:

- identical external actions produce byte-identical D10/D11 observations, masks, rewards, and
  terminal metadata through completion;
- deterministic D11 teacher labels diverge from D10 only after the exact empty-seed fallback
  predicate;
- every selected teacher action is legal;
- crop-before-scale, both fresh funding receipts, worker cap three, destruction cap three, and all
  prior D9/D10 invariants pass;
- D10 retains its frozen non-reacquiring teacher behavior; and
- consumed D11 teacher/random remain feasible and discriminative without changing the gates.

No gate, seed interval, task rule, expert predicate, checkpoint, or policy may change from
readiness outcomes.

## Fresh controls

Run teacher and random legal exactly once on unopened Level-5 seeds 6,000--6,499 with 100
environments, timeout 240, and random seed 113.  Teacher must reach:

- >=95% overall and nontrivial success;
- >=90% in every recipe and >=93% in every height;
- >=95% terminal player-crop presence and >=95% renewable player harvest;
- zero illegal selected actions and no success before turn 180;
- first-worker training >=98% and third-worker training >=90%;
- fresh receipts before 100% of both recorded training events;
- standard-chopper productivity >=98% and feeder productivity >=85%;
- exactly three terminal rival workers in every recorded third-worker episode and never more than
  three;
- crop creation before every third-worker event, rival crop creation >=98%, and rival own-crop
  harvest >=85%;
- at least one, two, and three confirmed player-crop destructions in >=98%, >=95%, and >=90% of
  episodes; and
- no episode above three confirmed destructions.

Random legal must remain <=5% overall.  Any control failure stops before actor replay, learning,
prospective seeds, deployment, YT writes, or Arena action.

## Fixed-actor gate

Only if every control passes, replay the unchanged accepted Level-4 checkpoint once on the exact
same interval against the D11 teacher artifact.  Require:

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

A pass authorizes one separately frozen prospective confirmation on unopened seeds
2,031,000--2,032,999 without learning.  A valid teacher plus actor failure establishes a recurrent
post-depletion recovery deficit and authorizes diagnosis plus a separately frozen clone/PPO
protocol.  D11 itself authorizes no checkpoint change, deployment, or Arena submission.

## Conditional compute decision

Controls and actor replay remain local.  Only a control-valid actor failure opens the previously
specified identical one-million-transition local/YT RTX 4090 benchmark with cold startup,
steady-state rollout, optimization, artifact transfer, total wall time, and effective throughput
reported separately.  Multi-million-transition YT replicas require a measured material advantage.

## Pre-implementation anchors

- stopped D10 result:
  `01e17cac60b6c06eda028812f2246036c83e05028f39dde2d818480f16460026`;
- rejected deadline screen:
  `de432830fb16561bb5ab01b176c940133833be6c0aec5b05b2f6f715889dcd58`;
- consumed reacquisition screen:
  `38f73561cfb6873cca9569e5595e3463920922ecb17edc2a400266e6deb452f7`;
- Rust source with unwired helper:
  `e30a29dcf050742ad6af3c504e304ec9403032aff38f900ae2bb8ec3ec692e56`;
- Level-5 environment:
  `353491ee78d59f3403c678f93062c6390aa07218ddefb6925ec11c9a478b6050`;
- PPO/evaluation selector:
  `711aefa2adb20719af4df9eeb5265224b32fc48b3e11041ca3a2cf3d7ef9f66c`;
- evaluator:
  `20a82651f318934001f994639e1944deac611d6240a814fb47174bf8b3640ec3`;
- focused tests:
  `ccf0b4355b179cf86ea66c0563b680be866c3b8995cf16adb3edcc07d983ba79`;
- release library:
  `afd1f4fbb405a66f2a260d25181f0025ecd22a584bcb2b648198e0f290c22f21`;
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- fresh Level-5 interval: `[6000, 6500)`, unopened at freeze; and
- reserved prospective interval: `[2031000, 2033000)`, unopened and inaccessible before a D11
  development pass.
