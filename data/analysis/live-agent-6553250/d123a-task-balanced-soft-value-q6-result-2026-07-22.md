# D123a task-balanced soft-value q6 — result

Date: 2026-07-22  
Decision: **close task-balanced objective without fresh simulation**

D123 changes exactly one part of D119: instead of assigning equal loss mass to every q6 root, it
assigns equal total rank and gate loss to every supported training task. Architecture, features,
temperature, 80-epoch deterministic fit, seeds, thresholds, offsets, retired 80-map audit panel,
and relative safety semantics remain fixed. Two complete executions produce the same result bytes.

The weighting implementation behaves as intended. All 235 supported tasks receive total weight
`5.629787` (floating-point range below `0.000001`), while individual root weights range from
`0.255899` to `5.629787` across 1,323 roots.

The isolated change fails the prospective structural gate on every seed:

| Seed | Mean proposal regret | Within 10 | Gate balanced accuracy | Act recall | Wait recall |
|---:|---:|---:|---:|---:|---:|
| 12301 | 19.122 | 41.57% | 65.52% | 72.19% | 58.86% |
| 12302 | 18.952 | 42.25% | 65.41% | 73.12% | 57.69% |
| 12303 | 18.893 | 42.48% | 65.42% | 73.59% | 57.25% |
| 12304 | 18.349 | 42.93% | 65.90% | 72.66% | 59.15% |

All four exceed the regret ceiling of 18 and miss the 45% within-ten floor. This reverses D119's
main achievement: its root-balanced models reached regret `16.659--17.235` and within-ten coverage
`45.80%--46.64%`.

The explicit retrospective audit nevertheless exposes a real trade-off. At offset `-1`, D123's
four models average `+3.158` margin at 88.98% activity. The strongest point, seed 12302, reaches
`+3.347`, 46.41% strict improvements, six positive families, and a `-1.869` floor. It fails only
the activity gate on the retired policy panel, in addition to the model's two structural failures.
At offset `+0.5`, average activity drops to 70.64%, but mean improvement falls to `+1.490`; all
four miss both the `+2` mean and 40% strict floors. None of the 24 policies passes all relative
held gates, and none is retrospectively eligible. All 24 exactly match control's 99.844% crop
rate, confirming D122's corrected safety semantics.

Conclusion: full task equalization over-corrects the root-density imbalance. It makes high-activity
policies stronger but damages proposal ordering enough to invalidate the model, and the coarse
offset grid jumps across the useful activity band. Do not collect fresh validation or retain a
checkpoint. The next bounded diagnostic should return to the structurally valid D119 models and
resolve the gate-offset interval on the retired panel. Its purpose is only to determine whether a
feasible calibration band exists; any deployable threshold must then be frozen by a prospective,
training-only rule and tested on genuinely fresh maps.

Lock SHA-256: `199cd8433d0f9325d376b918605a1e3d944b008d43034ba6a64a85f6eb0dba32`  
Result SHA-256: `44ca3e6d940828a68574b2d40d9e3671b86710261b8ee718c0afab9ad44a8841`
