# D128a absolute-value-anchored soft ranker — result

Date: 2026-07-22  
Decision: **close the shared-logit value anchor without fresh simulation**

D128 retains D119's 6,626-parameter factorized controller and adds the frozen root-balanced
smooth-L1 loss from every proposal logit to `act_advantage / 10`, plus a runtime requirement that
the winning proposal logit be positive. The first complete fit reaches result construction but
stops before writing an artifact because the metadata uses the JSON token `false` in Python. A
separately locked mechanics-only repair changes it to `False` and points verification at the
repair lock; no model, data, metric, threshold, seed, or decision changes. Two repaired executions
produce byte-identical result artifacts.

None of the four frozen seeds is fit-eligible:

| seed | proposal regret | within 10 | value-sign balanced accuracy | act recall | predicted-positive roots | fit intervention | fit mean |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12801 | 21.340 | 36.89% | 50.00% | 0.00% | 0.00% | 0.00% | +0.000 |
| 12802 | 21.699 | 36.36% | 50.00% | 0.00% | 0.00% | 0.00% | +0.000 |
| 12803 | 20.871 | 39.30% | 51.81% | 4.06% | 2.19% | 9.77% | +0.379 |
| 12804 | 21.364 | 36.43% | 53.41% | 8.44% | 4.91% | 18.75% | +1.109 |

Every seed misses both unchanged ranking gates: regret must be at most 18 and within-ten coverage
at least 45%. Every seed also misses the frozen value-sign balanced-accuracy and act-recall gates.
The coefficient-1 absolute regression term therefore does not merely calibrate D119's arbitrary
root-wise logit shift: it degrades relative ranking and, under the strongly negative proposal
distribution, drives almost every winning logit below zero. The best seed still acts on only
18.75% of fit tasks and remains far below the policy mean and strict-improvement gates.

Because fit eligibility is zero, the code does not score even the consumed D126 development
panel. Seeds `9,843,800--9,843,815` remain untouched. No checkpoint is emitted, no Rust integration
is started, and the platform is not contacted.

The next abstraction should decouple the two jobs that conflict in D128. Preserve D119's
soft-listwise ranker and state gate unchanged. Train a separate class-balanced proposal-safety
head to predict whether each exact proposal advantage is positive. At runtime discard proposals
whose safety logit is nonpositive, then choose the highest D119-ranked surviving proposal; wait if
none survive. This can reject or replace unsafe winners without forcing absolute calibration into
the ranking scalar. Develop it on fit data plus the already-consumed D126 panel before buying new
maps.

Original lock SHA-256: `6fd7f45c1d796624d670d00e6a020e061a6da09cb13fac8e1ba0db274c412a15`  
Repair lock SHA-256: `f1b7bdb7ec750f701d4892fb14480ded7b043213b4f8da7c1bf4f5651d1c9c3c`  
Result SHA-256: `cbbd12e33f2afb3f6c104ee5005034fb60470e853466a1af5f6f4fd2e5918300`
