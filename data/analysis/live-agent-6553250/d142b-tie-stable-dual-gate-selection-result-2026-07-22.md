# D142b tie-stable dual-gate selection — result

Date: 2026-07-22  
Decision: **close 50/50 dual gate on eight-block strict transfer**

D142a first confirmed exact component reproduction, then stopped without a selection artifact when
one averaged-logit quantile boundary tied. D142b's label-free total-order repair is used in only one
of 32 fold/seed calibrations. Every D140 and D141 component hash still reproduces exactly.

Two repaired selections are byte-identical (SHA `c3879c1d...`). Each takes 7m55s--7m58s, peaks at
2.38--2.44 GiB RSS, and records zero swaps. No seed clears the unchanged strict gate:

| pair | mean | strict | block floor | positive families | family floor | activity | failed gate |
|---|---:|---:|---:|---:|---:|---:|---|
| 13401/13701 | +3.218 | 38.13% | +0.875 | 8 | +0.809 | 68.51% | strict |
| 13402/13702 | +3.239 | 38.92% | +1.020 | 8 | +0.504 | 70.56% | strict |
| 13403/13703 | +2.980 | 37.45% | +1.328 | 7 | -0.270 | 70.65% | strict |
| 13404/13704 | +3.057 | 39.65% | +0.621 | 8 | +0.731 | 70.51% | strict |

Pair13404/13704 is the strongest eight-block result so far and is only eight strict wins short of
40% among 2,048 tasks. It is robust across independent halves: D133 is `+2.971`, 38.77% strict,
all families positive, and `+0.621` block floor; D139 is `+3.143`, 40.53% strict, all families
positive, and `+2.715` block floor. Composition helps but cannot be reinterpreted as a prospective
pass.

No full fit, D126 score, checkpoint, final validation, Rust integration, or platform action is
authorized. Result SHA is `9869e219...`; repair lock SHA is `e606e01a...`.

The next defect is objective/runtime alignment. D137/D141 mark only the single best positive root
per task, while runtime executes the first root above its calibrated boundary. Lowering that
boundary to reach the task-count target can admit earlier roots that the hard loss explicitly
labels negative even when their selected-winner value is positive. Freeze a slim single-gate
follow-up: keep the soft best-stop term, but label every valid root with positive selected-winner
value as hard-positive and apply equal-task/equal-class loss. The positive-task count and +3pp
calibration remain unchanged. Test on all eight blocks before D126.
