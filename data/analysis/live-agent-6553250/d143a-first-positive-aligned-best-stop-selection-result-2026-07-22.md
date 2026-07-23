# D143a first-positive-aligned best-stop selection — result

Date: 2026-07-22  
Decision: **close one-use gate refinements and pivot to offline multi-intervention value**

Two complete selections are byte-identical (SHA `ee5d7ca3...`). Each takes 7m47s--7m50s, peaks
near 2.40 GiB RSS, and records zero swaps. No seed clears the unchanged strict gate:

| pair | mean | strict | block floor | positive families | family floor | activity | failed gate |
|---|---:|---:|---:|---:|---:|---:|---|
| 13401/13701 | +2.876 | 38.33% | +0.898 | 8 | +0.063 | 69.24% | strict |
| 13402/13702 | +3.364 | 37.94% | +1.703 | 8 | +0.918 | 70.07% | strict |
| 13403/13703 | +2.998 | 37.60% | +1.387 | 8 | +0.270 | 69.53% | strict |
| 13404/13704 | +2.793 | 39.26% | +1.566 | 8 | +0.918 | 71.04% | strict |

The new label is learned: selected-positive roots constitute 17.75%--18.36% of held roots;
positive-root recall at zero is 46.72%--50.78% and negative-root recall is 77.57%--79.99%.
Every seed has all eight pooled families and every held block positive. The aligned hard target
therefore improves uniformity, but not strict policy transfer. Pair13404/13704 remains below the
D142b dual gate's 39.65% strict result.

D140--D143 now isolate evidence scale, calibration, root/task normalization, complementary gate
composition, and first-positive hard labels. None passes 40% strict across 2,048 out-of-fit tasks.
Another threshold, seed, or one-use gate loss would continue the same plateau.

No full fit, D126 score, checkpoint, final validation, Rust integration, or platform action is
authorized. Result SHA is `85ca40e3...`; lock SHA is `317b6e01...`.

Direct online Monte Carlo remains closed by measured latency (209/279 ms for shared-state search;
the first useful sparse horizon still exceeded the live budget). Preserve simulation as an offline
teacher. Next run a bounded prospective pilot on unused discovery seeds `9,844,128--9,844,135`:
compare the exact one-use oracle with a deterministic, capped two-intervention Monte-Carlo
population through the existing public q6 batch environment. Require material incremental value
and safety before collecting a large YT trajectory corpus or training a student.
