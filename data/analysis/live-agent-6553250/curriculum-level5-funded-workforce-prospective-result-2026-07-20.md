# Curriculum Level 5 naturally funded two-worker prospective result — 2026-07-20

## Verdict

**Accept D5 without learning.**  On the frozen, previously unopened exact interval
2,025,000--2,026,999, the teacher solves 1,999/2,000 = 99.95%, random legal solves 0/2,000, and
the unchanged accepted Level-4 actor solves 1,957/2,000 = 97.85%.  Every frozen control,
functional, stratified, workforce, funding, productivity, interaction, and paired-timing gate
passes.  No new checkpoint exists.

## Prospective controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **99.95% / 99.92%** | >=90% / >=88% | pass |
| Worst recipe / height | **99.63% / 99.80%** | >=82% / >=88% | pass |
| Player crop / renewable harvest | **99.95% / 99.95%** | >=92% / >=95% | pass |
| Illegal selected actions | **0** | 0 | pass |
| Opponent training / maximum workers | **96.40% / 2** | >=75% / <=2 | pass |
| Trained with verified funding receipt | **100%** | 100% | pass |
| Trained-worker productive activation | **92.95%** | >=60% | pass |
| Opponent crop / own-crop harvest | **94.45% / 79.40%** | >=65% / >=25% | pass |
| Confirmed player-crop destruction | **91.30%** | >=50% | pass |
| Destruction above one | **0** | 0 | pass |
| Random-legal overall | **0/2,000** | <=5% | pass |

The teacher completes at median turn 63.  The opponent trains at median turn 16, averages 22.501
confirmed productive trained-worker actions and 46.604 score, and never exceeds the frozen cap.

## Unchanged Level-4 actor

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **1,957/2,000 = 97.85%** | >=85% | pass |
| Nontrivial success | **97.80%** | >=82% | pass |
| Worst recipe | **96.61%** | >=75% | pass |
| Worst height | **97.01%** | >=80% | pass |
| Player crop / renewable harvest | **98.10% / 98.75%** | >=90% / >=90% | pass |
| Paired-teacher median delay | **0 turns** | <=20 | pass |
| Opponent training / maximum workers | **96.35% / 2** | >=75% / <=2 | pass |
| Trained with verified funding receipt | **100%** | 100% | pass |
| Trained-worker productive activation | **92.95%** | >=60% | pass |
| Opponent crop / own-crop harvest | **94.50% / 80.20%** | >=65% / >=25% | pass |
| Confirmed player-crop destruction | **91.10%** | >=50% | pass |
| Destruction above one | **0** | 0 | pass |

The actor completes at median turn 66 and the opponent trains at median turn 16.  Development and
prospective actor success are 97.80% and 97.85%, an absolute difference of only 0.05 points.

## Analysis at different abstraction levels

### Transaction

Ordinary resource acquisition and payment support a delayed standard chopper in more than 96% of
episodes before player-0 completion.  Every training event has a prior external funding receipt.
The empirical answer is therefore that additional workers are usually affordable; whether they are
profitable is a scheduler and role-allocation question, not a literal inability to pay.

### Parallel economy

The second worker is productively active in 92.95% and averages 25.238 confirmed productive actor
turns.  This occurs alongside 94.50% rival crop creation, 80.20% rival renewable harvest, and
91.10% player-crop destruction.  The actor's 97.85% success is not an artifact of dormant or
economically irrelevant extra workforce.

### Causal curriculum

Natural movement, planting, one-shot destruction, paid training, and bounded two-role parallelism
all transfer prospectively without learning.  The complete D0 collapse can no longer be attributed
to “the opponent has more than one worker” as a binary feature.  The next discriminator must test
workforce **scale** beyond two or broaden policy pressure while changing only one of those axes.

### Learning and compute

There is no D5 learning deficit worth fitting: the actor is stable across fresh banks, all strata
clear their floors, and paired median delay is zero.  A GPU/YT PPO run is therefore not authorized;
the highest-leverage next step is another small local causal experiment.

### Goal and transfer

D5 still supplies player 0's target recipe and cannot select a live opening or macro strategy.  It
does not produce an Arena-ready source or rank movement and authorizes no submission.

## Next hypothesis

Compare a naturally funded **third-worker** transition against this accepted two-worker base while
holding the first two roles and the one-player-crop-destruction cap fixed.  This isolates workforce
scale.  Repeated crop pressure or unrestricted policy scope should be tested only after that scale
question, unless third-worker teacher feasibility fails before actor replay.

## Reproducibility anchors

- prospective protocol:
  `15c5e4e24417ee64345c4695c7cdf5ef7576bd0e0775c84bf53eeea5f7bf2dc0`;
- teacher artifact:
  `0dd8cc547039805d3a9ce6843a5d594dd012c1a91cb73bd4e785038f50215d94`;
- random-legal artifact:
  `fd33c09383797efcdf2cb63d4d8f55ae14b0c84d697fef86428c052f4eef9da0`;
- fixed-actor artifact:
  `a60e085bb7535b9bf0f9cd18b5e830ac850b8e4353773ec3f943e0772bb02ccb`;
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`; and
- D5 development result:
  `8b21b990cd0d4c30f8d58033352f407f575bde33327ec0517a4a752e49be6049`.
