# D119a long-fit soft-value q6 ranker — result

Date: 2026-07-22  
Decision: **close after exhausted held coverage repair; locked policy outcome remains unobserved**

## Fit and validation

D119 changes only D118's deterministic training horizon from 40 to 80 epochs. Two complete
single-thread fits are byte-identical (`b9b8d8fb...`). All four 6,626-parameter models pass the
frozen structural gate: mean proposal regret is `16.659--17.235`, within-ten coverage is
45.80%--46.64%, and gate balanced accuracy is 65.29%--66.15%. Six fit policies are eligible.

The untouched 16-map validation panel contains 256 baselines, 1,475 roots, and 24,146 arms at
27.477 arms/s with 90.23% support and no mechanics failures. Four of 24 frozen seed/offset
candidates pass validation. The prospective robust order selects seed `11901`, offset `0.0`, and
model hash `a2a79d842732acf746225723754ebd3c54d7d95d3eefa43557c10f0f3002903f`.
It scores `+2.941` mean, 42.19% strict improvement, 83.98% activity, five positive families,
positive folds of `+2.359`/`+3.523`, and a `-3.375` floor. The exact checkpoint is 30,579 bytes.

## Held mechanics and bounded repair

The initial untouched 16-map held panel fails only the frozen 90% forced-control support gate:
220/256 tasks (85.94%). It otherwise has zero failures, 1,165 roots, 18,659 arms, and 33.832
arms/s. The locked policy is not scored. A separately frozen repair permits at most four
contiguous 16-map blocks and defers every teacher/policy computation until aggregate mechanics
passes.

Support by block is:

| Panel | Supported | Rate |
|---|---:|---:|
| Original held | 220 / 256 | 85.94% |
| Repair 1 | 228 / 256 | 89.06% |
| Repair 2 | 236 / 256 | 92.19% |
| Repair 3 | 226 / 256 | 88.28% |
| Repair 4 | 229 / 256 | 89.45% |
| Aggregate | 1,139 / 1,280 | 88.984% |

The terminal 80-map panel therefore misses 90% by 13 supported tasks. Every other mechanics gate
passes: 103,602 exact arms, 6,321 roots, complete grids, exact identities, one expert-bank hash,
zero provenance/accounting/direct-command failures, and 25.675 arms/s. The four-block cap is
exhausted, so D119 closes without computing the checkpoint's held metrics. This is not a policy
failure and does not authorize threshold waiver, a fifth block, Rust integration, Arena, or
submission.

## Conclusion and next hypothesis

Longer deterministic fitting solved D118's rank-quality gate and produced the first checkpoint in
this branch to transfer through untouched validation. The remaining blocker is now experimental
semantics: zero-boundary tasks are already valid forced controls, while a 90% *fractional* support
gate prevents evaluation despite 1,139 supported tasks and more than 100,000 exact arms.

The next bounded analysis should keep the checkpoint and every policy gate unchanged, treat the
80-map artifact as policy-outcome-sealed, and prospectively replace the percentage criterion with
absolute per-stratum information requirements justified by statistical precision. A diagnostic
pass may open quantized Rust integration plus a genuinely fresh final confirmation; it cannot
retroactively make D119 a held pass or authorize submission.

Fit artifact SHA-256: `b9b8d8fb327aad9a030c735ad65fcda9e38b97b7616f9227bf47f27b5387afd9`  
Validation result SHA-256: `551593926dd87034c9b87644d24a02cb378a54df7986a9a8c036eac101333cb8`  
Checkpoint SHA-256: `33d1e57642dcf7afaa26909be2681c86cb860627da9ba740881520e284a5c0e6`  
Held lock SHA-256: `aa8dc801509263a846b1a3cd6fb6b0721c1048cf0009474d708c05e464548241`  
Coverage-repair lock SHA-256: `499ec3b163406af1c7c99595fe0bc0b452a22668e984109453b43d4e28cf33f2`  
Terminal result SHA-256: `db72a199043de5e4b3281e4e77ebb1a5917d896952f728ece167c1057011e200`
