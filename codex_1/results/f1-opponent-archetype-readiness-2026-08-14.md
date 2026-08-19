# F1 opponent-archetype readiness result

**Verdict: `EARLY_PROXY_SIGNAL`**

This is a proxy-family signal audit only. It does not authorize adaptation, a bot change,
an experiment, TestSession, submission, or Arena action.

## Integrity

The restored 2,048-game source hashes to `9b7281fb374d229524afc8341cf119ff30b073c73121f0fd4d87b8597c2af6f4` and exact task coverage is `True`.
Overall integrity and leakage controls pass: `True`.

## Held-map results

| Turn | Linear cumulative macro-F1 | 95% map bootstrap | Top-2 | Min recall | Seat F1s | Centroid F1 | Current-only linear F1 | Static-map F1 | Permutation p99 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.800 | [0.778, 0.821] | 0.969 | 0.613 | 0.800 / 0.800 | 0.675 | 0.712 | 0.028 | 0.149 |
| 20 | 0.831 | [0.806, 0.855] | 0.972 | 0.691 | 0.831 / 0.831 | 0.722 | 0.768 | 0.028 | 0.150 |
| 40 | 0.922 | [0.906, 0.937] | 0.986 | 0.855 | 0.919 / 0.925 | 0.775 | 0.864 | 0.028 | 0.153 |
| 80 | 0.944 | [0.931, 0.956] | 0.992 | 0.895 | 0.940 / 0.947 | 0.815 | 0.888 | 0.028 | 0.154 |

## Turn-40 gate interpretation

The primary frozen model is standardized multinomial linear over cumulative legal history. Its serialized model plus feature schema is 15107 bytes and worst outer-fold single-example p95 inference is 0.012 ms.
For clarity, the offline Python audit path takes 2.690 ms p95 to rebuild all 40 observed transitions from scratch. That replay-rebuild cost is not the inference gate above; a live extractor maintains those transition totals as states arrive. This report is not an end-to-end Rust deployment benchmark.
Command/label deletion feature and prediction parity are `True` / `True`; portable-scorer prediction parity is `True`.

The exact per-family precision/recall tables, confusion matrices, nested choices, seat controls, 1,000 within-seed permutations, and all four horizon results are in the adjacent JSON.

A positive readiness verdict would authorize only a separately reviewed three-arm action-target audit. This report itself authorizes nothing downstream.
