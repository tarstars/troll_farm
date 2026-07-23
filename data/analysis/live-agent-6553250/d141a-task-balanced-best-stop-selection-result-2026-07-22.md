# D141a task-balanced best-stop selection — result

Date: 2026-07-22  
Decision: **close task-balanced hard-stop loss on eight-block transfer**

Two complete selections are byte-identical (SHA `4a6e9f20...`). Each finishes in 7m47s--7m51s,
peaks near 2.44 GiB RSS, and records zero swaps. No seed passes the unchanged strict-improvement
gate:

| pair | mean | strict | block floor | positive families | family floor | activity | failed gate |
|---|---:|---:|---:|---:|---:|---:|---|
| 13401/13701 | +2.584 | 37.94% | +0.863 | 8 | +0.410 | 68.80% | strict |
| 13402/13702 | +3.230 | 38.33% | +1.586 | 8 | +0.656 | 70.70% | strict |
| 13403/13703 | +2.878 | 37.79% | +1.551 | 8 | +0.281 | 69.73% | strict |
| 13404/13704 | +2.825 | 39.36% | +0.988 | 8 | +0.570 | 71.00% | strict |

The isolated mechanism works. D140 held positive-task recall at zero was 13.79%--16.23%, versus
81.13%--87.22% wait recall. D141 raises positive recall to 65.53%--70.70%; wait recall becomes
39.42%--44.62%. Equal-task/class-balanced loss therefore removes the root-count and negative-class
bias exactly as intended.

Transfer safety also becomes more uniform: every seed now has all eight pooled families positive
and every held block positive. Pair 13404/13704 reaches 40.14% strict on the independent D139 half,
versus 38.57% on D133. D140's root-weighted gate showed the complementary pattern, especially for
pair 13402/13702: 41.41% on D133 and 37.01% on D139. The task-balanced correction improves breadth
and reverses the corpus asymmetry, but does not alone improve pooled strict wins enough.

No full fit, D126 score, checkpoint, final-map validation, Rust integration, or platform action is
authorized. Result SHA is `7d1458ad...`; lock SHA is `364a962e...`.

Next test the complementary objectives without duplicating the ranker. Train the D140 root-weighted
and D141 task-balanced 689-parameter gates over one shared unchanged ranker, average their logits
exactly 50/50, and apply the same training-count calibration. This adds only one gate (7,475 total
parameters) and no extra ranker inference. Freeze the arithmetic mean and all eight-block gates
before fitting; D126 remains veto-only.
