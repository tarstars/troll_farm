# D137a task-sequence best-stop gate q6 — result

Date: 2026-07-22  
Decision: **close at held-block strict-rate gate; D126 remains unscored**

Two complete 16-fit selections are byte-identical (SHA `2a367aed...`) and take 99.44 and 101.79
seconds at about four CPUs. No pair is eligible, but all four now pass every block-mean, family-
floor, family-breadth, activity, crop, workforce, and directional gate. Every pair fails only pooled
strict gains:

| Ranker/gate | Mean | Strict | Block floor | Family floor | Families | Activity |
|---|---:|---:|---:|---:|---:|---:|
| 13401/13701 | +3.676 | 38.96% | +1.246 | +0.305 | 8 | 69.14% |
| 13402/13702 | +3.475 | 39.65% | +1.316 | +0.742 | 8 | 68.75% |
| 13403/13703 | +3.138 | 38.18% | +1.488 | +0.250 | 8 | 67.29% |
| 13404/13704 | +2.391 | 38.48% | +1.133 | -0.008 | 7 | 68.55% |

The exact positive-best-stop count is 513--551 of 768 training tasks depending on fold and ranker;
calibration transfers to 58.59%--75.78% activity by block and about 68% pooled. The task objective
therefore reduces D135's roughly 80% activity while making all block and family means consistently
safe. Held task-choice accuracy remains only 22%--31%, so the representation is not saturated.

The frozen 40% strict gate is missed by as little as 0.35 percentage points (four of 1,024 tasks).
Because D126 was never opened, the next isolated test may adjust only training calibration. Add a
fixed three percentage points to the exact positive-stop task count, retaining the same models,
objective, seeds, gates, and selector. This is a bounded guardband test, not a searched threshold
grid. Result SHA is `f1ab9ded...`; lock SHA is `8609f9d0...`.
