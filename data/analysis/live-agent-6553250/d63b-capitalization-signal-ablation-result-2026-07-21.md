# D63b capitalization-signal ablation result (2026-07-21)

## Verdict

**Pass the primary flow gate and the stricter instantaneous-state ablation.** D63a's held-agent
turn-100 signal does not depend on opening geometry, worker talents, first-TRAIN timing, or
cumulative action history. An instantaneous 44-feature economy snapshot ranks later third-worker
creation at validation AUC **0.993**.

Worker recipe also carries signal, but it is materially weaker. The next experiment should test
prospective value using the smaller instantaneous representation. D63b remains behavior prediction,
not a score claim, and creates no candidate.

## Frozen execution

D63b read the exact frozen D63a JSON and no replay or confirmation product. It retained the same
150 eligible rows and identity-held partition:

| Partition | Rows | Later third worker | No later third worker |
|---|---:|---:|---:|
| Discovery (9 agents) | 74 | 16 | 58 |
| Validation (11 agents) | 76 | 30 | 46 |

The stored 139-feature D63a reference metrics were verified exactly before fitting any ablation.
Seven focused D63a/D63b tests passed.

## Results

| Frozen representation | Features | Discovery AUC | Validation AUC | Validation balanced accuracy | Gate |
|---|---:|---:|---:|---:|---|
| Worker recipe only | 21 | 0.978 | 0.839 | 0.612 | Pass |
| Instantaneous economy only | 44 | 0.997 | **0.993** | 0.650 | **Pass** |
| Economy plus cumulative flow | 62 | 0.999 | **0.996** | 0.733 | **Pass** |
| Combined D63a reference | 139 | 1.000 | 0.970 | 0.783 | Pass (verified) |

At the frozen 0.5 threshold, the instantaneous model has 9 true positives, 46 true negatives, zero
false positives, and 21 false negatives in validation. The flow model has 14, 46, zero, and 16.
Both are conservative at that threshold but nearly perfectly rank positives above negatives. No
threshold was changed after observing this result.

## Interpretation at several levels

1. **Static recipe:** a harvest-capable second worker is associated with later scale, but recipe
   alone loses about 0.154 validation AUC relative to current economy.
2. **Instantaneous state:** deposited/carried PLUM, LEMON, and IRON plus a living fruit base contain
   almost all transferable ranking information. Cumulative behavior is not required.
3. **Flow history:** adding past planting/harvest/drop counts improves fixed-threshold sensitivity,
   but adds little ranking value (0.996 versus 0.993 AUC).
4. **Deployment:** the 44-feature snapshot is smaller, fully observable, and avoids maintaining
   history counters. It is the minimal passed representation for a prospective controller test.
5. **Causality:** the classifier predicts what strong policies do; it does not prove that scaling
   in the predicted states is beneficial. Exact paired intervention is now mandatory.

The leading instantaneous coefficients favor own IRON, carried and banked LEMON/PLUM, live LEMON
assets, and total ripe/fruit-bearing board assets. Carried and deposited WOOD enter negatively.
That is consistent with a transaction poised on renewable training currency rather than an idle
wealth threshold.

## Decision

Open D64 as a prospective, fresh-seed, paired late-capitalization test on the complete D40 macro
substrate. Preserve D40 identically before turn 100. If the controller still has two workers at its
first later TRAIN boundary, latch one of two actions: continue D40's third-worker plan or suppress
late scaling and keep both workers on productive jobs. Compare the fixed field-snapshot selector
with D40, never-late-scale, an inverse-selector negative control, and the two-arm hindsight upper
bound.

Use the frozen 0.5 classifier threshold. Do not tune it from D64 outcomes. No D64 setup or result
authorizes a platform action.

## Reproducibility

```text
a630a388e645902b61ea15882ee74d71038893f60913348920a3384dace0a627  d63b-capitalization-signal-ablation-protocol-2026-07-21.md
d38c8556401f9d71486778bd3335ddfd65b88e7d27b268426af1d0042f3f76bb  cgauto/analyze_d63b_capitalization_ablation.py
ac11370e7dd6b8783b0b9f3295bc3c70f2e37d8bcc45423e577135ea690f6f37  tests/test_analyze_d63b_capitalization_ablation.py
6970d5ae2949c71f32bcade6f992d39b2f1f984c15d73b1f4593cbceaf5db059  d63b-capitalization-signal-ablation-2026-07-21.json
```

