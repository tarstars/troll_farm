# D126a rank-quality-selected calibrated q6 — result

Date: 2026-07-22  
Decision: **close the fixed D126 controller without validation tuning**

D126 changes only D125's seed selector. The 84% training-activity quantile remains exact, while
the lowest proposal-regret rule selects seed11903 at offset `-0.1012164876`. Two complete fit
artifacts are byte-identical. The selected fit policy has `+7.746` mean, 53.13% strict gains,
83.98% activity, all eight families positive, a `+0.625` floor, and proposal regret `16.659`.

The untouched validation range `9,843,780--9,843,795` was then collected once with 20 workers.
It contains 256 baselines, 1,494 roots, and 24,341 exact arms. Support is 238/256 = 92.97%; all
integrity gates pass with zero mechanical failures, and throughput is 26.027 arms/s against the
12 arms/s floor. The complete score reproduces exactly.

Fresh policy result:

| Metric | Result | Gate |
|---|---:|---:|
| Mean margin delta | **+2.828** | >= +2, pass |
| Strict improvements | **42.58%** | >= 40%, pass |
| Fold means | +1.664 / +3.992 | both >= 0, pass |
| Activity | 83.98% | 10%--85%, pass |
| Positive families | 6/8 | >= 6, pass |
| Worst family | **-4.281** | >= -3, **fail** |
| Own / opponent score delta | +2.266 / -0.563 | directional, pass |
| Crop rate | 100%, equal to control | relative safety, pass |
| Worker-three rate | 93.75%, equal to control | relative safety, pass |

Family means are resident `+2.781`, compact `+2.719`, gold `+9.844`, silver `+2.813`, legend
`+10.625`, mybot `+1.844`, script `-3.719`, and norx `-4.281`. Thus the controller has real broad
fresh value, but its two negative families violate the frozen tail guarantee. The failure is not a
coverage, throughput, activity, crop, workforce, fold, or overall-value artifact.

Do not lower the `-3` gate, retain a checkpoint, integrate, or use the newly authorized platform
for this failed controller. The panel is now consumed and may be used only for retrospective
mechanism analysis. Next trace loss concentration by task, chosen proposal type, turn, gate logit,
and exact counterfactual value across norx/script; simultaneously sweep only the already-consumed
threshold frontier. The purpose is to distinguish a global calibration repair from an observable
state/action safety rule before freezing another fresh test.

Fit result SHA-256: `80a2a8045dc4449d8b93f288de7ea5119a86ca3312d3f16e8443b48513574265`  
Selection lock SHA-256: `a862b25906278360789851a030621e115da1a25207af60e52a8b585a7e1030c2`  
Validation arms SHA-256: `1c2f3b69f802e08b58119a8af728ea225c0560f9bcf88c182b3978b0b294a96d`  
Validation baselines SHA-256: `72f6bfca3f9c2635416cf4c17d0f6a93c0d129e43517c0993e89d215160a713c`  
Result SHA-256: `f34c32d9efdfab2ab8f1bccb762a99ba800319522a8b38d43da805cef218b8c6`
