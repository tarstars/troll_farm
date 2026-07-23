# D29c official-field activation audit — result (2026-07-20)

## Verdict

**Failed; D29b is not eligible for Arena transfer.**  The exact frozen D29b selector was replayed
read-only on the first 80 resident games fixed before inspection.  Only 7/80 roots selected the
farm option (`8.75%`), below both preregistered activation gates: at least ten observations for
each decision and an activation rate between 17% and 67%.

This is a representation-transfer failure, not a numerical, protocol, or runtime failure.  No
Arena submission occurred and the stable resident remains unchanged.

## Frozen sample and integrity

- expected, fetched, and replayed games: 80 / 80 / 80;
- roots reaching turn 75: 80;
- agent/submission identity failures: 0;
- unknown replay updates: 0;
- non-finite predictions: 0;
- roots outside the exact two-own-worker support: 0; and
- observed decisions: 7 switch, 73 stay.

The sample was the first 80 game IDs in the frozen 171-game resident checkpoint.  The protocol and
its gates were written before fetching their replay payloads.  A first execution exposed a uniform
diagnostic-harness type error; it produced no usable predictions.  The harness was corrected and
the same frozen sample was rerun without changing the protocol or gates.

## Distribution shift

The converted raw prediction distribution moved sharply negative relative to the untouched D29b
generated confirmation set:

| Distribution | Mean | Median | p05 | p95 | Activation |
|---|---:|---:|---:|---:|---:|
| Generated confirmation (1,920 roots) | -13.690 | -12.070 | -134.869 | 112.763 | 42.135% |
| Official resident trajectories (80 roots) | -91.735 | -84.800 | -223.629 | 19.010 | 8.750% |

The official mean shifted by `-78.045` raw points and the median by `-72.730`.  The closest official
prediction was `7.406` points from the strict `+4` threshold; zero roots were within one or four
points.  Quantization noise or strict-boundary handling therefore cannot explain the collapse.

Both seats show the same pattern: seat 0 switched 3/47 (`6.38%`, mean raw `-90.41`) and seat 1
switched 4/33 (`12.12%`, mean raw `-93.62`).  A player-orientation error is not supported.

The shift is also present across observed resident outcomes:

| Outcome cohort | Games | Switches | Mean raw prediction | Mean observed margin |
|---|---:|---:|---:|---:|
| Catastrophic loss | 7 | 1 | -97.73 | -209.71 |
| Ordinary loss | 31 | 2 | -98.48 | -30.13 |
| Win | 42 | 4 | -85.76 | 62.21 |

These outcome rows are descriptive only.  They do not estimate what the unplayed farm branch would
have scored on those roots.

## Interpretation at different levels

1. **Artifact and protocol:** complete.  Identity, replay coverage, finite inference, worker guard,
   and exact implementation checks all passed.
2. **Numerical decision boundary:** ruled out as the primary cause.  Predictions are far from the
   threshold, and both seats agree.
3. **State distribution:** failed.  Real Legend turn-75 states occupy a prediction regime far more
   negative than the generated training and confirmation roots.
4. **Model validity:** unresolved.  The audit does not distinguish a valid response to genuinely
   different states from extrapolation by the scalar or spatial branch.
5. **Policy value:** unmeasured on official roots.  Recorded resident outcomes cannot supply the
   missing farm counterfactual.

## Decision and next hypothesis

The frozen D29b controlled-transfer protocol is closed.  Do not rescue it by retuning its threshold
on these 80 games.

D30 will treat these 80 games as a development-only diagnostic set.  It will first decompose the
prediction shift into scalar-history, spatial-state, and interaction components, then identify
which features are out of generated support.  Any new selector or calibration must be frozen before
inspection of a disjoint official checkpoint suffix and must pass a new prospective gate.  The
remaining resident games are not silently folded into D29b tuning.

## Reproducibility

- protocol: `d29c-official-field-activation-audit-protocol-2026-07-20.md`;
- machine result: `d29c-official-field-activation-audit-2026-07-20.json`;
- checkpoint SHA-256:
  `a8d43f58b5150bb42c0d5630cb02e1c342a04a7c34d1ca0d708aa1b1fc2aef38`;
- diagnostic binary SHA-256:
  `c71d510940be2e4328a1a9f9e642fb107333d38b00693c59284d8cadc799d39b`; and
- machine-result SHA-256:
  `97affd3fb389039fc4d24e4f0fef97ddb8f75d9ac4e2430d4c8e3451c9654a4b`.
