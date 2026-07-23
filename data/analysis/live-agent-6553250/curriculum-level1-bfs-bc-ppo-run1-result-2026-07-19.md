# Curriculum Level 1 BFS + BC + PPO run-one result — 2026-07-19

## Verdict

Run one passes the frozen Level 1 gate after an exact-seed integrity correction.  The final PPO
checkpoint solves 992/1,000 exact held-out seeds, 99.10% of nonzero-deficit episodes, and at least
98.81% in every map-height bucket.  Its median successful completion is 42 turns, equal to the
exact teacher median.  This authorizes the already specified independent Level 1 replicate.  It
does not authorize an Arena submission or replacement of the resident.

The stronger causal conclusion is narrower: BFS proximity planes plus a teacher bootstrap solve
the destination-selection failure that made PPO from scratch unusable.  PPO recovers from its
early regression, but run one does not show an overall advantage over the behavior clone itself.

## Integrity correction

The original batched evaluator stopped after the first 1,000 completed episodes.  Because an
environment slot resets immediately, episode duration could leave a slow nominal-bank seed in
flight while admitting a later seed.  The nominal `2,000,000--2,000,999` evaluations contained
975 nominal seeds; Stage A and Stage B still shared 991/1,000 seeds, but they were not a strictly
paired bank.

The evaluator, teacher/random runner, and action auditor now retain only seeds in the exact closed
interval requested and continue until all of them finish.  Two regression tests assert the exact
ordered seed interval.  Eight focused tests pass.  The original artifacts remain immutable audit
evidence; corrected artifacts use the `-exact` suffix.  No model was retrained, no threshold was
changed, and the correction was applied before the replicate bank was opened.

## Exact results

All learned rows below are the frozen checkpoints reevaluated on exactly seeds
`2,000,000--2,000,999`.

| Policy | Overall | Nonzero deficit | Height floor | Median turn | Deficit 8 | HARVEST selection | DROP selection |
|---|---:|---:|---:|---:|---:|---:|---:|
| Exact teacher control | 99.80% | — | 99.60% | 42 | — | — | — |
| Exact random-legal control | 10.40% | — | 9.68% | 1 | — | — | — |
| Official behavior clone | 99.30% | 99.21% | 98.80% | 42 | 97.35% | 75.95% | 100% |
| PPO Stage A, 250k | 97.20% | 96.86% | 95.63% | 44 | 96.46% | 74.95% | 100% |
| PPO Stage B, 1M | 99.20% | 99.10% | 98.81% | 42 | 98.23% | 71.86% | 100% |

The final PPO policy gains 20 successes over Stage A and restores the teacher median.  Relative to
the clone, however, it loses one overall success while gaining one success in the hardest
initial-deficit bucket.  That is statistical parity, not evidence that PPO is already superior.
The critic nevertheless learns a useful return representation: explained variance rises from
negative at initialization to roughly 70% late in training.  This may matter when Level 2 adds
real decisions that the teacher did not prescribe.

Run cost was 1,296.93 wall seconds for one million PPO transitions, 69.88% aggregate host CPU, and
771 end-to-end transitions/s including four-epoch optimization.  Raw rollout throughput was
usually 4,000--6,600 steps/s.  Fourteen Torch threads remains the measured sustainable setting.

## Analysis at different abstraction levels

### Representation

The two BFS proximity planes are the decisive change.  With the same 104x11x22 tensor and 34,926
parameters, behavior cloning moves from the from-scratch policy's near-total waiting failure to
99% closed-loop coverage.  The shallow spatial head can act globally once distance is explicitly
represented.

### Learning algorithm

Teacher initialization is necessary at this level; PPO from scratch is closed.  Pure PPO
fine-tuning is stable but initially destructive and only returns to clone-level coverage near the
end of the linear schedule.  The replicate should test reproducibility, not tune PPO from run-one
curves.  If Level 2 regresses, retaining a teacher auxiliary loss becomes the eligible response.

### Experiment design

Completion-order sampling was a subtle policy-dependent selection mechanism.  Exact seed-set
membership is now an invariant for every control, audit, and learned gate.  Run-one gates still
pass by wide margins after correction, but the independent exact replicate is the first clean
confirmation experiment.

### Contest strategy

Level 1 has a waiting opponent, one fixed target worker, automatic TRAIN requests, and no strategic
worker allocation.  It validates navigation, harvesting, dropping, and learning infrastructure;
it says nothing yet about renewable supply, multiple roles, opponent denial, or live transfer.
The known fast-engine movement-tie drift also remains.  A learned policy cannot approach the
resident until it passes richer curricula, exact-engine parity, and the layered top-five field
gate.

## Frozen artifacts

- behavior clone: `34579adff653980fcd47cdea54e5cf55fb6346f294959cff2a6f68ced13aa25f`
- Stage A checkpoint: `519907d5db70c15199990c1f583c19272f341218828a916373cd60c3cbbe39e3`
- Stage B checkpoint: `b345508ec45d1b67360d199106f6b53fdd9f62a90bcd2d8d37a6a7385e3277a7`
- exact teacher control: `934261b115321b0a81331824b2547b6939cdaf9fdadc1ed20aa6b37efe8bbe5f`
- exact random control: `3fbd41a3b0482cd8f9b57c1d24f7c3436c60c6d5185def6f7f9cc0414a7a4de5`
- exact clone audit: `7c303822a789f678b2ddb663becbbff8851527e9e2f2d868cfc2b9c52c09e902`
- exact Stage A audit: `426dee4dec71550106b189a4b8fd310d030703e5e805ce44957818a462c98360`
- exact Stage B audit: `712112ee1bd54a41d24303f2ca684043cb9c0c7605f1d34950e3f6bc26c97566`

## Decision and next move

Run the frozen exact-seed replicate with model seed 47, BC stream beginning at 3,000,000, PPO stream
beginning at 3,100,000, and the unopened exact evaluation bank
`2,001,000--2,001,999`.  A replicated pass advances to randomized-worker Level 2.  Failure closes
the current initialization/schedule pair and triggers diagnosis on consumed banks only.

