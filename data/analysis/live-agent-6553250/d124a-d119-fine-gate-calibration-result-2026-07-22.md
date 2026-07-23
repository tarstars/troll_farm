# D124a D119 fine gate calibration — result

Date: 2026-07-22  
Decision: **design a prospective training-only gate-calibration rule**

D124 exactly reproduces the four structurally valid D119 models and scores the pre-frozen 44-point
grid: offsets `-0.50` through `0.00` at `0.05` resolution on the retired 80-map panel. Every point
is also checked against the unchanged training-policy gates, relative aggregate safety gates, and
nonnegative mean margin in each of the five fixed blocks. Two complete executions produce the
same result bytes.

Three points pass every descriptive gate:

| Candidate | Fit mean | Fit activity | Aggregate mean | Strict | Activity | Families | Floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11903 / -0.10 | +7.766 | 83.98% | +2.548 | 40.94% | 79.61% | 7 | -0.881 |
| 11903 / -0.05 | +6.969 | 82.03% | **+2.782** | **41.02%** | 78.05% | 7 | -0.956 |
| 11904 / -0.05 | +5.547 | 84.38% | +2.109 | 40.78% | 80.78% | 6 | -0.931 |

The descriptive-best point, seed 11903 at `-0.05`, is positive in every block: `+2.820`, `+2.375`,
`+2.027`, `+3.453`, and `+3.234`. It improves own score by `+1.205`, reduces opponent score by
`1.577`, exactly matches control's 99.844% crop rate and 90.859% worker-three rate, and has no
family below `-0.956`.

This resolves the apparent plateau at the model level. D119's ranker has a stable useful band; the
original half-logit grid skipped it. The band is not a new candidate because it was discovered on
consumed data. The useful points share a simple training-side signature—82.03% to 84.38% fit
activity—which can be specified without held outcomes.

Next freeze a model-independent calibration rule targeting 84% intervention on the original fit
tasks. Derive each model's threshold from the empirical per-task maximum gate-logit quantile, then
choose among structurally and policy-valid seeds using the existing robust fit selection key. Only
after the rule and fresh seed range are locked may it be tested on new validation maps. D124 itself
authorizes no checkpoint replacement, integration, Arena action, or submission.

Lock SHA-256: `91d9203a3c0944f51cbadf06266537d021eb36a6799415764d7438f6f953e690`  
Result SHA-256: `48745f26f26007d956e7c223bf7e9f44acf752c1824330b3063214c060b6482d`
