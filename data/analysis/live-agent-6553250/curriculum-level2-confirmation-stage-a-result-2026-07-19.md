# Curriculum Level 2 confirmation Stage-A diagnostic — 2026-07-19

## Verdict

**Healthy diagnostic; continue unchanged.**  On the prospective confirmation bank at 500,000
transitions, the seed-67 run exceeds even the stricter discovery Stage-A thresholds.  The frozen
confirmation protocol makes this a non-stopping diagnostic, so the same process continues to two
million transitions.

| Metric | Discovery Stage-A reference | Observed |
|---|---:|---:|
| Overall success | >=70% | 94.15% |
| Nonzero-total-deficit success | >=65% | 93.55% |
| Recipe-family floor | >=60% | 85.41% |
| Height floor | >=55% | 91.63% |
| Paired teacher median delay | <=30 turns | 0 turns |

Family success is 95.70%, 96.02%, 97.02%, 93.72%, 99.24%, 95.08%, 91.74%, and 85.41% in
catalog order.  The hybrid chopper is again hardest, independently reproducing the discovery
difficulty ordering.  The policy solves 1,883/2,000 exact episodes at a median 14 turns.

Frozen checkpoint SHA-256:
`44b9d02a30c409cc4ea5db55b9cc4a59073f3972ee77b2d4f3e601d20a39ea0b`.
Evaluation SHA-256:
`5865f7e72068ccd13f92a39533b2ae7b16e0228f651be7fe482f71cd80a4c617`.

## Next move

Continue the unchanged optimizer, streams, auxiliary coefficient, and learning-rate schedule to
two million transitions.  Decide confirmation from the predeclared final outcome floors and exact
action-collapse audit, not from this intermediate read.
