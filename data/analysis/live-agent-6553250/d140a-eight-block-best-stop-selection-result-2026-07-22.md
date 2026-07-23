# D140a eight-block best-stop selection — result

Date: 2026-07-22  
Decision: **close unchanged D138 controller on eight-block transfer**

Two complete eight-fold selections are byte-identical (SHA `c74dc1b1...`). The shared read-only
fork implementation finishes each selection in 7m50s--7m53s, peaks at about 2.42 GiB RSS, records
zero swaps, and keeps four one-thread fits concurrent.

No seed pair clears the frozen held gates:

| pair | mean | strict | block floor | positive families | family floor | activity | failed gates |
|---|---:|---:|---:|---:|---:|---:|---|
| 13401/13701 | +2.969 | 38.18% | +0.793 | 7 | -0.098 | 69.73% | strict |
| 13402/13702 | +3.300 | 39.21% | -0.160 | 8 | +0.797 | 71.14% | strict, block |
| 13403/13703 | +3.065 | 38.18% | +1.469 | 7 | -0.086 | 70.90% | strict |
| 13404/13704 | +2.912 | 38.48% | -0.004 | 8 | +0.523 | 69.92% | strict, block |

The independent halves expose real transfer loss. Pair 13402/13702 scores `+4.273`, 41.41%
strict, all eight families positive, and a `+1.984` block floor on D133 blocks 0--3. On D139
blocks 4--7 it falls to `+2.327`, 37.01% strict, seven positive families, and a `-0.160` block
floor. Every seed has a lower strict rate on D139 than D133. More maps therefore corrected the
four-block selection optimism instead of merely changing the selected seed.

The controller's raw task classifier is strongly asymmetric. Across seeds, held positive-task
recall at zero is only 13.79%--16.23%, while wait recall is 81.13%--87.22%. Training sequences
average 5.54 roots and reach 25 roots. D137's hard-stop BCE is averaged over all valid roots, so
long tasks and their many negative roots receive more weight than short tasks even though policy
quality and strict improvement are task-level metrics. D138's count offset can repair activity but
cannot repair this within-task ordering.

No full fit, D126 score, checkpoint, fresh-map validation, Rust integration, or platform action is
authorized. Result SHA is `7929d2bc...`; lock SHA is `940f484d...`.

Next isolate the loss normalization defect while retaining the eight-block evidence, architecture,
ranker loss, seeds, +3pp calibration, gates, and selector. Replace only flattened hard-stop BCE
with an equal-task loss: each task contributes one mean hard-stop loss regardless of root count,
and within positive tasks the one positive root and the task's negative roots receive equal class
mass. Repeat exact eight-block selection before any D126 veto.
