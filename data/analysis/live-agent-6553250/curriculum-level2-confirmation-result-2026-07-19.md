# Curriculum Level 2 independent confirmation result — 2026-07-19

## Verdict

**Pass; Level 2 accepted.**  The disjoint seed-67 clone/PPO run clears every frozen confirmation
outcome and action-quality gate on exactly seeds 2,007,000--2,008,999.  It also clears all of the
stricter discovery thresholds, providing a strong independent replication rather than a marginal
confirmation.

This accepts the curriculum abstraction only.  The learned policy still receives a requested
recipe, controls only the starter troll, and relies on the environment to submit TRAIN.  It cannot
replace the resident or authorize an Arena submission.

## Prospective final result

| Metric | Confirmation gate | Observed | Result |
|---|---:|---:|---|
| Overall success | >=85% | 98.60% | pass |
| Nonzero-total-deficit success | >=80% | 98.30% | pass |
| Recipe-family floor | >=70% | 94.66% | pass |
| Height floor | >=70% | 97.41% | pass |
| `MOVE current` waits | <=40,000 | 2,105 | pass |
| Needed productive choice rate | >=60% | 97.21% | pass |

The policy solves 1,972/2,000 maps at median turn 14.  Family success in catalog order is 99.22%,
99.20%, 100%, 99.16%, 100%, 97.54%, 99.57%, and 94.66%.  Every height bucket is at least 97.41%.
The exact action audit observes 4,407 legal, currently needed HARVEST/MINE opportunities and takes
the productive verb in 4,284.  It takes DROP in all 5,774 states where DROP is legal.

The teacher is 99.95% overall and random legal is 40.70%; the learned policy is therefore +57.90
points over random with zero paired teacher median delay.  These are diagnostics under the
confirmation protocol, but independently match the discovery result.

## Replication analysis

| Metric | Seed-61 discovery | Seed-67 confirmation | Difference |
|---|---:|---:|---:|
| Overall success | 98.15% | 98.60% | +0.45 pp |
| Nontrivial success | 97.98% | 98.30% | +0.32 pp |
| Recipe floor | 95.58% | 94.66% | -0.92 pp |
| Height floor | 97.40% | 97.41% | +0.01 pp |
| Productive choice | 93.87% | 97.21% | +3.34 pp |
| Idle-current moves | 2,377 | 2,105 | -272 |

The near-identical aggregate performance and repeated hybrid-chopper difficulty ordering show that
the result is architectural, not a favorable seed/model accident.  The coefficient-0.10 teacher
auxiliary also reproduces its intended mechanism: final teacher-action accuracy is 93.8%, entropy
0.200, and deterministic productive-choice behavior does not collapse.

Training completed 2,000,000 transitions in 2,082.10 wall seconds and 28,965.23 CPU-seconds,
equivalent to 69.56% aggregate capacity on the 20-core host.  Throughput is 960.57 transitions/s,
and final critic explained variance is 0.630.

## Frozen artifacts

- final checkpoint: `8a831f6f7878eef898af4377530c291e577cc58750860c20c89a9005a5e19926`;
- exact evaluation: `0ada2a2900f6a7d591d63952f83ffd433bb56c8f50411c346c8505801df632fd`;
- exact action audit: `e9b276ff099e3261f2ea9b907bd2266143f15cb8e66961cc561ddc8f2291427f`;
- training summary: `9ad85a8ab4f8f46a2ff54b28d55b2fd94d6d04868728598c31e8a37a5f7f860b`;
- protocol: `74e7b4dc1d7fe714bcc650ac6185b57bfdffc1f374048149ea5eadc7f22f0355`.

## Next move

Freeze the smallest next abstraction that closes one transfer gap without conflating all remaining
ones.  The preferred Level 3 is a two-troll renewable-work objective: retain a fixed requested
worker recipe and automatic TRAIN, but expose both resident trolls to the policy and require them
to produce a renewable score/resource target after training.  Recipe selection and opponent play
remain later levels.  This directly tests whether the accepted funding policy can become a
complete multi-worker economy.
