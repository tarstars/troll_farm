# D83a threatened-response value predictability result (2026-07-21)

## Verdict

**Reject and close the fixed pooled snapshot ridge model.** The held-map OOF policy gains +1.188
mean margin, but misses the frozen +2 floor, strictly improves only 24.72% of rooted tasks versus
30%, and fails opponent-family breadth. No full model is serialized and no fresh closed-loop bank
opens.

Do not tune ridge penalty, threshold, features, folds, arm weights, or reuse D82 labels for another
fit. D83a creates no candidate and authorizes no platform action.

## Export and fit integrity

- Two 1,168-row feature exports are byte-identical at SHA-256
  `17d2ca501204baa026e2c388a8d550b5251479e4b75206317a04bca93f15bbeb`.
- All 512 control roots and 656 available semantic arms match D82 root identity, availability,
  exact-prior rank, action plane, own provenance, opponent proximity, and semantic one-hot.
- All 169-feature values, ridge fits, and predictions are finite; every arm receives one prediction
  from a model that excludes its map fold.
- Two complete OOF fits/predictions are bit-identical. Three focused trainer tests and the broader
  D79--D83 analyzer suite pass.

## Held-map result

| Metric | Result | Frozen gate |
|---|---:|---:|
| Mean selected margin gain | **+1.188** | >=+2 — **fail** |
| Strictly improved rooted tasks | **24.72%** | >=30% — **fail** |
| Regressed rooted tasks | 20.04% | <=30% |
| Mean own-score delta | -0.338 | own >=0 or opponent <=0 |
| Mean opponent-score delta | **-1.525** | own >=0 or opponent <=0 |
| Intervention rate | 45.88% | 10%--70% |
| Nonnegative map folds | 6/8 | >=6; worst >=-5 |
| Nonnegative opponent families | **5/8** | >=6; worst >=-3 — **fail** |

Family means are +5.781 Legend Balanced, +2.672 Silver, +2.219 Gold Adaptive, +1.594 Compact Gold,
and +1.359 native Norxondor, but -0.141 Script Boss, -0.672 MyBot, and **-3.313 resident**. The
selector uses fell 158, renew 30, harvest 18, and abstains 306 times; response breadth and
intervention-rate gates pass.

## Predictability diagnosis

Across individual available arms, prediction correlation with true terminal delta is only 0.0185
Pearson and 0.0460 Spearman. Predicted-positive precision is 53.97%, barely better than an
unconditional coin at this support. The OOF policy captures only **10.56%** of D82's +11.240 oracle
headroom.

The small positive policy mean comes primarily from control abstention and broad suppression, not
accurate ranking. It is useful evidence that abstention contains regressions, but not enough to
justify a prospective model. This reproduces D42's deeper lesson under a better action vocabulary:
rich current snapshot features expose the opportunity set, yet individual terminal continuation
value remains weakly predictable from a static linear boundary.

## Next experiment

Move from snapshot prediction to actual bounded counterfactual search. At a fresh threatened-own-
crop root, roll each semantic response under a small resettable opponent-proxy ensemble from the
current referee/scheduler state, then test whether proxy rollout ranking predicts the paired actual
continuation arm. Begin with fidelity and measured latency only; do not construct a live controller
until the ensemble materially captures D82-like oracle value under held opponents and fits the
turn-time budget.

## Evidence

- protocol SHA-256: `7f44611f0f38dd272ab7ee4daf30dd3c3d2e0e740f99e9e13381265fc5ef5e41`;
- result JSON SHA-256: `068c0d18adb7734c7bcfe21c1a80284566b0cd163b63f4611bc163365a370254`;
- feature export SHA-256: `17d2ca501204baa026e2c388a8d550b5251479e4b75206317a04bca93f15bbeb`;
- exporter SHA-256: `5fc03ded5aac52d27ea3f20612a3acffe5ad5008a024dcf38b74c4824a855a73`;
- trainer SHA-256: `935866ccee3469cd88abe7a9658b5bb132cb744dc3e44ef6c3b837d4d54d79ac`.
