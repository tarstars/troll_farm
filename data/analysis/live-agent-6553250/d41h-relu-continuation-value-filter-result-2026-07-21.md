# D41h tiny-ReLU continuation-value filter — result (2026-07-21)

## Verdict

**Reject the frozen nonlinear representation and close consumed-label classification over the
existing 100 features.** None of 36 grouped target/width/decay/share candidates passes discovery,
so the D41d external replication is correctly skipped and no weights are created.

The best model is close but unqualified. The width-8 positive classifier with weight decay 0.01 at
50% coverage selects 281 rows, has mean continuation value **+14.690**, normal 95% lower bound
**+10.336**, 199 below-boundary rows, early/late means **+23.683/+5.887**, positive means in all
eight map folds, and a worst opponent mean of -0.200. Its negative rate passes at **25.98%**, but
its positive rate is **63.35%** against the frozen 65% floor. It misses by five positive outcomes;
that proximity does not authorize changing the gate or rerunning another seed.

## Frozen execution and integrity

- exact input archives: 600 x 100 D41f discovery rows and 126 x 100 unopened D41d external rows;
- three targets, widths 8/16, two weight decays, eight whole-map folds, and 600 full-batch Adam
  epochs: 12 configurations and 96 grouped fits;
- three frozen coverage shares per configuration: 36 evaluated candidates;
- all archives are finite, contain all eight folds, and have unique sample identities;
- seven focused D41g/D41h feature, target, determinism, raw-export, size, and gate tests pass; and
- 55.062 seconds wall time, with no simulator outcome or platform action.

Because grouped discovery has zero passes, full-data fitting, deterministic repeat, raw deployment
conversion, external scoring, complete-policy evaluation, confirmation, candidate construction,
TestSession, submission, and Arena all remain closed.

## What changed relative to the linear filter

At the same 50% coverage and n281, D41g's strongest adequately sized linear result had +17.83 mean,
+12.33 lower bound, 60.5% positive, and 30.2% negative. D41h's best sign classifier trades some
mean value for better separation: positive rate rises about 2.85 points and negative rate falls
about 4.22 points. It passes every gate except the positive-rate floor.

The improvement confirms that interactions matter, but it does not establish that more hidden
units or another optimizer seed would solve the remaining error. Every one of 36 candidates misses
positive precision, and 33 also miss negative precision. Width 16 is generally worse than width 8,
while stronger regularization is generally better; extra capacity on the same state description is
therefore a low-value continuation.

## Multilevel conclusion

- **Causal/action level:** the early/late rank-one rate reservoir remains real and broad. Selected
  actions retain large positive mean value and stable map/opponent breadth.
- **Statistical level:** the blocker is sign precision, not value magnitude, coverage, phase value,
  map-fold stability, or opponent specialization.
- **Representation level:** the 100-vector describes the two candidate jobs but omits much of the
  context that makes a spatial job safe: current and opposing workforce positions/carry, both
  inventories, active parallel jobs, target geometry/competition, and live plant state. A nonlinear
  layer can only partially reconstruct those missing variables from action IDs and ETA/rate.
- **Policy level:** D41e still demonstrates +4.116 complete-policy value, but neither a scalar gap nor
  the current compact feature representation can add the needed coverage at frozen reliability.
- **Engineering level:** the tiny model is cheap and deterministic; compute and source size are not
  the current constraint.

## Next eligible direction

Do not add widths, epochs, losses, seeds, thresholds, hand-selected crosses, or ensembles on D41f or
D41d. The next experiment must use a fresh continuation bank and freeze a compact context-complete
representation before observing its outcomes. Preserve exact D40 outside early/late rate choices.
The new representation should add explicit spatial contention and live economy/workforce context,
then face grouped discovery, disjoint external continuation replication, and only afterward a fresh
complete-policy gate.

## Evidence

- protocol SHA-256: `c24a981e23bc95551d98aba6b165d440d1ea004e88ebf17b6184c671d3ed0652`;
- result JSON SHA-256: `a92b00f7bcad26dc7047ba4d46b0893fd64a1115e5755e103c0910d846c72b91`;
- trainer SHA-256: `7d22140d6ce417c0559c0b2e1855e0e4c30928bb572505bdfa3b686a40a806f8`;
- test SHA-256: `8cf243016ab0514e4fd8968196edb81a0b2809721b79573fcb4f79df5fe12b84`.
