# D17 resident residual precision distillation — development result (2026-07-20)

## Decision

**Reject the 116-feature scalar distillation formulation.  Zero validation thresholds pass the
frozen gate, so the locked test remains unopened and no exact policy prototype is authorized.**

The negative result does not invalidate D16's counterfactual teacher.  It localizes the failure:
coarse deployable summaries can rank some useful interventions, but cannot separate them from
harmful lookalikes with the required cross-map precision.

## Complete execution

The exact teacher produced all 34,560 planned labels with mandatory per-scenario clone fidelity:

| Split | Maps | Labels | Positive | Negative | Random mean advantage |
|---|---:|---:|---:|---:|---:|
| train | 160 | 23,040 | 4,105 (17.82%) | 5,445 | -0.805 |
| validation | 40 | 5,760 | 939 (16.30%) | 1,365 | -0.746 |
| locked test | 40 | 5,760 generated | **unopened** | **unopened** | **unopened** |

Nine fixed models and three fixed three-seed ensembles were trained: linear binary, two-layer
binary MLP, and two-layer clipped-value MLP.  The distiller evaluated only the precommitted six
selection rates on validation.  No validation recipe met every precision, value, coverage, and
catastrophe gate, so the code did not read, hash, featurize, or score the locked test file.

## Closest recipe

`binary_mlp_s1703` at the 2% target selection rate was the strongest robust near miss:

| Measure | Result | Gate |
|---|---:|---:|
| Selected | 116 / 5,760 | at least 72 |
| Positive precision | **48.28%** | **at least 70% — fail** |
| Conditional mean advantage | **+1.983** | **at least +2.0 — fail by 0.017** |
| Map-clustered contribution CI | **[+0.0069,+0.0846]** | lower bound above zero |
| New catastrophes | 0 | 0 |
| Positive coverage | 26 maps, 6 opponents, both roles | pass |

At 1% the same seed reached +2.53 conditional advantage and 51.72% precision, but selected only
58 labels.  At 0.5%, another binary seed reached 68.97% precision on 29 labels, still missing the
sample, role, precision, and clustered-confidence gates.  This pattern says the representation
contains a weak ranking signal, not a safe decision boundary.  The value models sometimes found
high mean gains but also admitted large losses and occasional new catastrophes.

## Abstraction-level interpretation

- **Teacher level:** positive alternatives remain stable in frequency across the larger train and
  validation blocks, so D16 was not a density accident.
- **Statistical level:** the best scalar model has a positive aggregate contribution estimate, but
  only about half its selected actions are beneficial.  A few large wins compensate for many
  mistakes; that is unsuitable for direct policy transfer.
- **Representation level:** action verb, inventories, worker stats, local plant state, and intent
  history are insufficient to distinguish terminal consequences.  Missing spatial relations and
  route/resource geometry are the most plausible omitted information.
- **Algorithm level:** more PPO or a looser threshold would not address the observed ambiguity.
  The next experiment must add state information, not merely optimize this scorer longer.
- **Submission level:** D17 produces no runtime policy and changes nothing in the stable resident.

## Next hypothesis

Reconstruct the exact 137-plane observation at the already-labeled decision points and test a
small spatial scorer on new map-disjoint validation data.  Preserve the precision-first abstention
semantics and the locked-test discipline.  To keep source size practical, compare a tiny
convolutional encoder with compact engineered spatial distances; only a representation that
materially improves validation precision may proceed to a fresh locked block.

## Evidence

- training rows SHA-256:
  `3e8ab92a29bff9c7e2586afcfe9d7518eb1e79fa6404b840c9b60618c3210182`;
- validation rows SHA-256:
  `f502253f1e72671ca9cc8dbd88b62d3ab28b09e480212e2b6ebfc342a9d52588`;
- analysis SHA-256:
  `8205691544cfbbfe7200ee40fba9439b425ed0e23cc16ebbca506e6706aeb99a`;
- distiller SHA-256:
  `0fdd6e43fe7437f87aba63bef3c4bfe86880d300fda84d5b851c1d1237c59a54`;
- locked test SHA-256 deliberately omitted because the test was not opened.
