# Curriculum Level 5 naturally funded two-worker D5 result — 2026-07-20

## Verdict

**Pass D5 development without learning.**  On fresh seeds 2,500--2,999, the teacher solves
499/500 = 99.80%, random legal solves 0/500, and the unchanged accepted Level-4 actor solves
489/500 = 97.80%.  Every preregistered functional, stratified, workforce, funding, productivity,
interaction, and paired-timing gate passes.  No clone, PPO transition, checkpoint selection,
deployment, YT operation, or Arena action occurred.

## Fresh controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **99.80% / 99.65%** | >=90% / >=88% | pass |
| Worst recipe / height | **98.41% / 99.19%** | >=82% / >=88% | pass |
| Player crop / renewable harvest | **100% / 100%** | >=92% / >=95% | pass |
| Illegal selected actions | **0** | 0 | pass |
| Opponent training / maximum workers | **97.00% / 2** | >=75% / <=2 | pass |
| Trained with verified funding receipt | **100%** | 100% | pass |
| Trained-worker productive activation | **92.80%** | >=60% | pass |
| Opponent crop / own-crop harvest | **93.80% / 79.00%** | >=65% / >=25% | pass |
| Confirmed player-crop destruction | **90.80%** | >=50% | pass |
| Destruction above one | **0** | 0 | pass |
| Random-legal overall | **0/500** | <=5% | pass |

The teacher completes at median turn 61.  The opponent trains at median turn 15, averages 22.244
confirmed productive trained-worker actions, 46.774 score, 0.956 created crops, and 4.928 own-crop
renewable harvests.  The one teacher failure is retained in the aggregate result and was not
inspected before the control decision.

## Unchanged Level-4 actor

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **489/500 = 97.80%** | >=85% | pass |
| Nontrivial success | **96.83%** | >=82% | pass |
| Worst recipe | **95.08%** | >=75% | pass |
| Worst height | **96.83%** | >=80% | pass |
| Player crop / renewable harvest | **97.80% / 99.00%** | >=90% / >=90% | pass |
| Paired-teacher median delay | **0 turns** | <=20 | pass |
| Opponent training / maximum workers | **96.60% / 2** | >=75% / <=2 | pass |
| Trained with verified funding receipt | **100%** | 100% | pass |
| Trained-worker productive activation | **93.60%** | >=60% | pass |
| Opponent crop / own-crop harvest | **94.60% / 81.00%** | >=65% / >=25% | pass |
| Confirmed player-crop destruction | **91.40%** | >=50% | pass |
| Destruction above one | **0** | 0 | pass |

The actor completes at median turn 62 while the opponent trains at median turn 14 and averages
25.414 confirmed productive trained-worker actions.  Its lowest recipe is the Level-1 anchor at
95.08%; no recipe or height approaches its frozen floor.

## Analysis at different abstraction levels

### Resource transaction

The second worker is not free and is not merely bought from a favorable opening wallet.  Every
successful training event follows a verified harvest-or-mine deposit, pays the referee's ordinary
5/5/1/5 cost, and occurs at median turn 14--15.  This directly resolves the apparent contradiction
between “a dedicated worker is unaffordable” and strong bots using many workers: the transaction is
affordable in most games, while profitability depends on the worker's subsequent role and the
opportunity cost of the resources and actions used to create it.

### Workforce and scheduling

The trained chopper is not idle: it acts productively in 93.60% of actor episodes and averages more
than 25 confirmed chop/drop actions.  The starter simultaneously establishes and harvests a crop.
Thus D5 genuinely exercises role parallelism rather than merely increasing a roster counter.

### Interaction

The opponent trains in 96.60%, destroys the tracked player crop in 91.40%, creates its own crop in
94.60%, and harvests that crop in 81.00% of actor episodes.  Nevertheless actor success is 97.80%,
essentially unchanged from D4's prospective 97.90%.  A paid second worker plus sustained natural
chopping is therefore not the discontinuity behind D0's 51.80% result.

### Curriculum and architecture

The accepted actor already interprets opponent workforce and board changes well enough for this
bounded two-role economy, despite never training on D5.  Learning now would fit an 11-episode tail
instead of testing the next missing mechanism.  The remaining D0 gap lies in scale or policy scope:
additional workforce transitions, unrestricted task switching, repeated crop pressure, or their
composition.

### Goal and transfer

D5 is still a supplied-recipe curriculum, not an autonomous macro controller or Arena candidate.
It provides causal evidence for strategy design but no direct live-rank evidence and authorizes no
resident replacement or submission.

## Decision

Freeze one exact prospective confirmation on unopened seeds 2,025,000--2,026,999 under the same
opponent, telemetry, player lifecycle, checkpoint, and gates.  No learning is authorized.  A pass
accepts naturally funded two-worker interaction and moves the curriculum to the smallest remaining
scale/scope discriminator.

## Reproducibility anchors

- D5 protocol:
  `37c8f4ca00d247a16b55db4fa16b1aea80aac0471320c257ab9273efa9da7b52`;
- implementation readiness record:
  `3f21f96630cb6520cb9005ae3bb26ef9e3262365a8b066cd2d06cdf0d8cf723e`;
- teacher artifact:
  `2560f3cca004be15269d9197cc276485212e0c7f5c359b4c36cbcc0a8cf117c3`;
- random-legal artifact:
  `abdaf36c1f681e9614b3930019cf3f46177552845b4f2ed918a29e65b94bb2c4`;
- fixed-actor artifact:
  `42444a0230a0793835dd9a067f91d0a39fe340097f8a2013757c59bc608c0e1a`;
- Rust source / release shared library:
  `09b201e5b388e7d2391463670c0c9116289866a71caf94e5c13837b4bdf5521b` /
  `1d1752d8681302e1e7006ea82cd7338f56c8e36c4767c3ba9b1d78ae9bf4dd38`; and
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
