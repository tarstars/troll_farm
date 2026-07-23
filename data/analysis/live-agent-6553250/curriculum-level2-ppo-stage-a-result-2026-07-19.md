# Curriculum Level 2 PPO Stage-A result — 2026-07-19

## Verdict

**Pass; continue unchanged.**  Teacher-anchored PPO improves the seed-61 clone on the exact fresh
bank and clears every frozen 500,000-transition gate.  The run continues automatically to two
million transitions; this intermediate result does not authorize confirmation or deployment.

## Exact seeds 2,005,000--2,006,999

| Metric | Stage-A gate | Observed |
|---|---:|---:|
| Overall success | >=70% | 95.80% |
| Nonzero-total-deficit success | >=65% | 93.86% |
| Recipe floor | >=60% | 87.84% |
| Height floor | >=55% | 94.60% |
| Paired teacher median delay | <=30 turns | 0 turns |

Recipe success is 99.15%, 100%, 99.58%, 93.68%, 99.21%, 94.05%, 93.98%, and 87.84% in catalog
order.  The hybrid chopper remains the correct hardest family, but its result is 8.67 percentage
points above the behavior clone's consumed-bank floor.  Overall success improves from the clone's
89.90% consumed-bank read to 95.80% on a fresh bank; this cross-bank comparison is descriptive,
while the frozen gate itself is prospective.

Frozen Stage-A checkpoint SHA-256:
`f068dac9595a085ce9ef51a7d819eb2df9d9b429d197d40808c45b95bd2df783`.
Evaluation SHA-256:
`09e4a7661e5609e19c686fc641633676231d94bfe8d5f7a9bd2f28a2d49e2972`.

## Next move

Continue the exact process, optimizer, seed stream, auxiliary coefficient, and learning-rate
schedule to two million transitions.  Do not inspect or tune individual failed seeds.  At final,
apply the frozen overall/nontrivial/recipe/height/delay gate and then the exact productive-action
audit.
