# D155a first-action-memory value ablation — result

Date: 2026-07-23  
Decision: **close static first-action-memory value models**

The join is exact: all 909 conditional groups carry their D148 selected first action, all first
slots are nonzero, and 908/909 first-action feature rows are unique. Both 160-fit replicas are
behavior-identical with zero model-hash drift; every snapshot control reproduces D154 exactly.

Explicit first-action memory does not restore transfer:

| Architecture | Params | Median value | Median harmful | Median sign BA | Best cell |
|---|---:|---:|---:|---:|---:|
| snapshot compact | 1,873 | +1.699 | 45.82% | 52.07% | +2.089 |
| history concat compact | 2,689 | +1.037 | 44.88% | 51.95% | +1.424 |
| history bilinear compact | 2,688 | +1.405 | 45.54% | 51.89% | **+2.164** |
| history concat full | 13,185 | +0.913 | 44.72% | 51.36% | +1.433 |
| history bilinear full | 13,184 | +0.897 | 44.22% | 51.06% | +1.284 |

The best history cell gains only +0.075 over the matching snapshot cell, remains 46.31% harmful,
captures 7.12% of oracle value, has a negative fold, and misses the family floor. Larger full
history models are worse. The exact immediately prior intervention is therefore not the missing
causal variable for this per-action regression objective.

Stop expanding snapshot/history MLP inputs. The next cheap pivot is a deterministic coarse semantic
policy: estimate cross-fold value by job/owner class with hierarchical state-regime backoff and
natural control abstention. This tests whether exact target-cell return noise hides a stable macro
action class. If that also fails, prioritize online rollout/search or genuinely recurrent control.

No checkpoint or candidate exists. Reserved maps remain sealed; no YT, Arena, submission, or
resident mutation occurred. Result JSON SHA: `0ca37164...`.
