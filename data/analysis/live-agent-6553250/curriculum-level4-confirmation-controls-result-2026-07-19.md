# Curriculum Level 4 confirmation controls — 2026-07-19

## Verdict

Valid and discriminative.  The complete exact confirmation bank was generated only after its
protocol was frozen and before any confirmation learning labels were consumed.  The deterministic
teacher clears every prospective bank-validity floor; seed-89 random legal never completes the
objective.

| Metric | Teacher | Random legal | Teacher validity floor |
|---|---:|---:|---:|
| Overall success | 2,000/2,000 (100%) | 0/2,000 (0%) | 98% |
| Nontrivial success | 100% | 0% | 97% |
| Worst recipe success | 100% | 0% | 95% |
| Worst height success | 100% | 0% | 95% |
| Tracked crop created | 100% | 19.10% | 98% |
| Renewable harvest | 100% | 1.50% | 98% |

All eight teacher recipe families and all four map-height buckets score 100%.  Teacher median
training/completion turns are 14/51 and median post-training score gain is 15.  Random legal has
median training turn 1, no successful completion turn, and zero median score gain.

## Reproducibility anchors

- frozen protocol:
  `ea4c66a270effb9040db17b2476e61bcf88f1edf2719051f6ffea42571022596`;
- exact teacher control:
  `bcabf56f69353c10e4945765c80d8f576443f121616bb294af736e56f4006ca2`;
- exact seed-89 random-legal control:
  `6f46f36441c52221d6acb7c3d1a6bf87720ce29767da0581da7fc27677a7052c`.

The interval is exactly 2,017,000--2,018,999 with no seed omissions.  The bank now remains fixed
for clone, Stage-A, final functional evaluation, and strict action audit.

## Authorized next execution

Start the independently seeded 800,000-label transfer clone from the accepted Level-3 checkpoint,
using model seed 89 and online stream 6,800,000.  No discovery checkpoint or data may initialize
the clone.
