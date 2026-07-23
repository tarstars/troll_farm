# Curriculum Level 5 D11 fixed-actor action diagnosis — 2026-07-20

## Verdict

The D11 deficit is a **spatial source-selection failure**, not failure to recognize that recovery
requires movement and not a general collapse of the two-role controller.  On exact seeds
6,000--6,499, the unchanged accepted actor succeeds in 79.40% of episodes.  In 13,963 decisions
where its post-training farmer has no crop, no carried item, and no home banana inventory, it
chooses the teacher's MOVE verb 13,952 times (**99.921%**) but chooses the teacher's exact source
cell only 998 times (**7.147%**).

This diagnosis changes the next experiment from an undirected PPO run to a teacher-anchored
spatial-target transfer test.  An online behavior clone gets the first opportunity to repair the
coverage hole.  PPO and YT are conditional on that clone failing preregistered outcome and action
gates.

## Exact-bank evidence

The audit replays checkpoint
`curriculum-level4-random-recipe-renewable-confirmation-ppo-l4b.pt`, SHA-256
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`, against D11 on the
already consumed development interval `[6000, 6500)`.

| Measure | Fixed actor |
|---|---:|
| Overall / nontrivial success | 79.40% / 76.67% |
| Crop / renewable harvest | 79.60% / 83.60% |
| Farmer exact productive choice | 35,618 / 64,610 = 55.13% |
| Farmer productive verb choice | 62,014 / 64,610 = 95.98% |
| Chopper exact productive choice | 80,031 / 84,940 = 94.22% |
| Chopper productive verb choice | 84,375 / 84,940 = 99.33% |
| Empty-seed recovery exact source | 998 / 13,963 = **7.15%** |
| Empty-seed recovery MOVE verb | 13,952 / 13,963 = **99.92%** |
| Combined unjustified current-cell waits | 2,233 |

Recovery exact-source rates are 6.53%, 0.24%, 0.17%, 0.00%, 11.84%, 5.81%, 14.53%, and
10.28% across the eight recipe families.  Compact-farmer, balanced-producer, and
harvest-producer therefore provide especially strong counterexamples to a claim that the actor
already knows the source-selection rule.

## Interpretation by abstraction level

### Command semantics

The actor almost always knows that it should move.  Adding a recovery flag or a new action verb is
not justified by this evidence.

### Spatial policy

The actor's MOVE logit is concentrated on the wrong legal cell when the best replacement source
depends on map geometry, source readiness, and travel distance.  Exact target supervision is the
most direct intervention.

### Role composition

The trained chopper remains strong, and all D11 opponent-activation gates pass under the actor.
Retraining the whole architecture is permitted only as an implementation convenience; acceptance
must demonstrate recovery-target lift without sacrificing the chopper or weakening the opponent.

### Curriculum

Earlier curricula contain initial planting and bounded replanting, but not enough examples after
crop, carried seed, and home seed are simultaneously absent.  D11 supplies those states naturally
without changing observations, actions, reward, or opponent pressure.

### Optimization and compute

Online behavior cloning can generate exact source labels cheaply and deterministically.  The
expensive PPO/YT path has positive expected value only if supervised transfer cannot meet the
frozen D11 gates.  A raw increase in training duration without a recovery-specific audit would not
test the diagnosed mechanism.

## Next hypothesis

> Starting from the accepted Level-4 checkpoint, 800,000 D11 teacher decisions are sufficient to
> raise exact empty-seed source selection from 7.15% to at least 30%, cover every recipe at at least
> 10%, and lift recurrent-pressure success above 90% without degrading the established chopper or
> opponent interaction.

The separately frozen D11 learning protocol tests this hypothesis.  Failure opens
teacher-anchored PPO and the local/YT throughput benchmark; success skips both.

## Reproducibility anchors

- action audit:
  `f7c2a4461e3dcc257f93d9af2014ca6c4925942374706204f336d7245a98b50f`;
- audit implementation:
  `dccaa98da556e693d502d052d4879945b41adf2a8efdae923990eea16de41277`;
- audit tests:
  `dfe65766d9e7f201e2bf5e7cefde5c017ef36d629ca97fb25776b75ddd87ac59`;
- D11 development result:
  `247a17d9d523e1a97f41f2596ac77d18e80cbffb35dfdab1c0b1500046e847c1`; and
- accepted checkpoint, unchanged:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
