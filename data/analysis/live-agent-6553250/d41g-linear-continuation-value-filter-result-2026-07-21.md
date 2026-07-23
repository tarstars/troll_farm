# D41g compact linear continuation-value filter — result (2026-07-21)

## Verdict

**Reject the linear representation.** Exact extraction succeeds for all 600 D41f training states
and all 126 eligible D41d replication states, but none of the 60 frozen target/regularization/share
combinations passes grouped discovery. External replication is therefore correctly skipped and no
weights are promoted.

The failure is narrow but systematic: every combination misses both the 65% positive-rate and 27%
maximum-negative-rate gates. This is not a mean-value, map-stability, phase, breadth, coverage, or
feature-integrity failure.

## Exact feature audit

- training matrix: 600 x 100, finite, zero missing states, zero replay/feature mismatches;
- external matrix: 126 x 100, finite, zero missing states, zero replay/feature mismatches;
- opponent identity is absent by construction;
- whole maps remain together in each of eight cross-validation folds.

The stored feature archives have SHA-256
`881cbbe5c4a1c86eeb3954604d30889380671ffa4da4c7ec62e62659605d5f1b` and
`c8c0aa33fc2c22406edff837c878fb95863ecee001fc5cb2f28c54e9e9128d69`.

## Best grouped results

The strongest lower-bound model is clipped-100 ridge with alpha 10 at the 40% share:

- n225, mean +20.98, lower bound +14.53;
- 61.3% positive and 28.0% negative;
- 163 rows below gap 0.280.

It fails the n240, 65% positive, and <=27% negative gates. At the required coverage, clipped-100
ridge alpha 0.1 and 50% share reaches:

- n281, mean +17.83, lower bound +12.33;
- early +20.58 and late +10.00;
- every map-fold mean positive, worst fold +9.69;
- every opponent mean above -1.75; and
- 199 rows below 0.280.

It still has only 60.5% positive and 30.2% negative. All 60 combinations fail those same precision
conditions; only the 12 undersized 40% variants fail sample count, and only 12 broad variants fail
the phase floor. The linear score clearly ranks expected magnitude, but cannot model the interaction
that separates positive from negative continuations.

## Next hypothesis

Close all affine variants over this 100-feature representation. The evidence supports exactly one
bounded nonlinear follow-up: a tiny one-hidden-layer ReLU scorer, still using the same exact features,
map-grouped folds, no opponent identity, and the unchanged coverage/precision/external gates. It may
model interactions among state phase, job kind, ETA, rate, and candidate contrast while remaining
well below the deployment budget.

Do not add linear targets, alphas, hand-selected feature crosses, or new thresholds on the consumed
banks.

## Evidence

- protocol SHA-256: `eaf0263d07af14c67ce0b8aebb9e02ebaef4f4f2d2abf89541de31232fbb41ff`;
- result SHA-256: `eda493c1fa62ecfbc800dba197cc13a553b9217e4db66d4eae183f982f734c9c`;
- trainer/analyzer SHA-256: `f9f89f275b1c1c816b793c0eeb22316c52f62b1e063495a296f086fe0c6969e6`;
- focused verification: six feature/ridge/boundary tests pass.
