# D41f early/late rate-boundary one-deviation study — result (2026-07-21)

## Verdict

**Reject a scalar lower-threshold expansion, but retain the newly proven action-value region for a
richer feature selector.** Two bins below D41e's 0.280 boundary independently pass every useful-bin
gate. No cumulative threshold passes because positive-outcome rates remain 56--57%, below the
frozen 60% reliability floor.

No complete policy, D41e Stage B, confirmation, deployment candidate, TestSession, submission, or
Arena action is opened by this result.

## Fresh execution and integrity

The outcome-blind manifest replayed D40 on maps 9,772,000--9,772,031, both seats, and all eight
opponents. Of 84,156 decisions, 21,399 were actionable early/late rate states and 994 lay in the
frozen gap range. Task-deduplicated sampling produced 600 interventions across 311 tasks.

All 600 states replay exactly. Two independent 96-row repeats are behaviorally identical and match
the corresponding full-run subset. There are zero legality, direct-command, provenance, relevant
prediction, or worker-cap failures.

## Bin results

| residual gap | n | mean margin | normal 95% low | positive | verdict |
|---|---:|---:|---:|---:|---|
| [0.100,0.200) | 38 | +1.947 | -3.079 | 47.37% | fail |
| [0.200,0.240) | 107 | +10.299 | +3.007 | 57.01% | fail n |
| [0.240,0.260) | 138 | **+11.058** | **+4.941** | **59.42%** | **pass** |
| [0.260,0.280) | 154 | **+12.032** | **+6.396** | **56.49%** | **pass** |
| [0.280,0.300) | 111 | +8.865 | +0.697 | 54.95% | fail n/rate |
| [0.300,0.320) | 48 | +9.896 | +0.018 | 58.33% | fail n |
| [0.320,0.340] | 4 | -0.750 | -10.298 | 75.00% | sparse fail |

Residual-gap magnitude is therefore not monotonically calibrated to action value. The two newly
useful bins are at least as valuable in mean as the original >=0.280 region.

## Cumulative thresholds

The strongest broad pool begins at 0.240: 455 samples, +10.626 mean, +7.150 lower bound, early
+16.213, late +4.444, and opponent breadth/tail pass. Its positive rate is only **57.36%**, so it
fails the 60% gate. Starting at 0.200 gives 562 samples, +10.564 mean and +7.429 lower bound, but
57.30% positive. Every scalar threshold fails the same reliability condition; higher thresholds
also become undersampled.

Across all 600 rows, one deviation improves margin +10.018 on average, adds +4.508 own score,
removes 5.510 opponent score, and reduces catastrophes by 16. Early value is much larger (+16.287)
than late value (+4.193), but both are positive with lower bounds above zero.

## Multilevel conclusion and next hypothesis

- **Proposal:** rank-one early/late rate actions contain broad causal value down to about 0.200.
- **Calibration:** residual gap orders PPO preference, not outcome probability; a single cutoff
  cannot remove the roughly one-third negative tail.
- **Coverage:** D41e can plausibly gain the missing 65 changed episodes from the [0.240,0.280)
  region, but unconditional activation would violate the reliability gate.
- **Next representation:** train a small continuation-value filter from shared state plus D40/rank-one
  candidate-feature contrasts. Group validation must hold out whole maps, exclude opponent identity,
  and require both expanded below-0.280 coverage and higher positive precision before any new
  complete-policy evaluation.

Do not lower D41e's threshold directly or weaken the 60% condition.

## Evidence

- protocol SHA-256: `b1a6fa7437f2f370db7401e07ab1e30f504637a7e357bc5eb524dc7e86074ded`;
- manifest SHA-256: `cb11caf22afae681268083bc8658f7a8ea3ba877e81c8cc9199ed83578425243`;
- continuation rows SHA-256: `3bbc1c62a5383c3d8667c40ba7173026ded60721ec41d0db72fb6d021fe09d26`;
- analysis SHA-256: `2860de6af912c46aa40b1e868790fa5629d28daa7cd83f7c4224e3815dd55e8b`;
- focused verification: six manifest/analyzer/replay tests pass.
