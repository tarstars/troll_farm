# D110a robust one-use q6 linear population — result

Date: 2026-07-22  
Decision: **mechanics pass; no discovery admission; held panel remains sealed**

## Execution and integrity

D110a evaluates the frozen 64-vector antithetic population on untouched seeds
`9,838,000--9,838,015`, both seats and all eight opponents. The validated 20-worker runner writes
256 exact D40 baselines and all 33,024 matched controller rows in 1,231.66 population seconds at
26.81 episodes/s after 40.81 seconds of baseline construction.

The population reconstructs exactly from seed `11001`. The grid is complete; every zero row exactly
reproduces D40; all returns are finite; paired reward error is zero; all intervention, proposal,
endorsement, job, provenance, and budget counters reconcile; and direct-command, provenance, and
deposit failures are zero. All 64 one-use policies preserve 100% crop creation and stay within the
worker-three safety floor.

## Discovery value

No one-use policy clears every frozen admission gate. Consequently no policy is selected, no
selected population is emitted, and untouched seeds `9,839,000--9,839,031` remain unexecuted.

The population contains real but incompletely controlled signal:

- 34/64 policies have positive mean gain;
- 10/64 reach the `+1.5` mean screen;
- 18/64 have nonnegative means in both interleaved map folds;
- 32/64 keep every family at least `-5`;
- 22/64 make at least five families positive; and
- 29/64 lie in the frozen 10%--85% task-activity band.

Three policies clear all five core value/stability tests, but every one acts too broadly:

- `one_03`: `+2.316` mean, 46.88% strict wins, `+1.734` minimum fold, six positive families,
  `-4.406` worst family, and 90.23% activity;
- `one_26`: `+1.969` mean, 46.09% strict wins, `+1.133` minimum fold, five positive families,
  `-3.375` worst family, and 90.63% activity; and
- `one_41`: `+2.020` mean, 42.19% strict wins, `+1.281` minimum fold, six positive families,
  `-2.844` worst family, and 88.28% activity.

Other near misses expose the same tradeoff. `one_55` gains `+2.152` at 78.91% activity but has
only four positive families. `one_61` gains `+1.996` with a `-2.625` floor at 80.47% activity but
has one negative map fold. The most balanced active policies remain below the mean or strict-win
screens.

## Conclusion and next hypothesis

The sparse authority change fixes repeated-intervention saturation but random outcome-aware
selection does not jointly solve value, abstention, and family robustness. Importantly, the useful
linear region is not absent: one random controller misses the discovery rule only by nine active
tasks and already clears the stricter future `-3` family floor. The binding frontier is calibrated
abstention, not crop/workforce safety or q6 proposal support.

Close D110 random selection exactly as frozen. Do not inspect four-use outcomes, weaken the 85%
ceiling, choose a near miss, move its threshold, or open held seeds. A distinct next test may
optimize whole policies from scratch on new maps with activity and worst-family terms inside a
prospective lineage objective. It must retain actual policies rather than average weights, cap
authority at one, and use rotating map blocks plus a separate selection panel to prevent the
D76/D77 collapse pattern.

Discovery result JSON: `64333cf8d29743281c25be481b1470c4d817a24dd3d90dd6a7021c51d7f6321b`  
Discovery rows: `22567de119b84c7ed89bbb9c297fb9e93696421bcf5c25aa7e9e4fedbadbcfef`
