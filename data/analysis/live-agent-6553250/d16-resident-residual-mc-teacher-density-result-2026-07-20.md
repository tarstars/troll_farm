# D16 resident residual Monte Carlo teacher density — development result (2026-07-20)

## Decision

**The frozen density gate passes.  Exact one-intervention labels are sufficiently frequent and
distributed to justify a larger, map-disjoint corpus and precision-first supervised
distillation.**

This authorizes offline label generation and distillation only.  D16 is not a policy, candidate,
submission, or Arena result, and the stable resident remains unchanged.

## Complete execution

The runner traversed the all-`KEEP` trajectory in all 240 frozen scenarios and evaluated ten
uniformly reservoir-sampled legal alternatives per scenario.  All 2,400 continuations completed.
The runner's mandatory clone check passed in every scenario: starting from a sampled clone and
returning to `KEEP` exactly reproduced the scenario's resident terminal signature.

| Measure | Result |
|---|---:|
| Positive terminal-margin labels | **429 / 2,400 (17.88%)** |
| Margin gains of at least +2 | **388 / 2,400 (16.17%)** |
| Ties | 1,455 / 2,400 (60.62%) |
| Negative labels | 516 / 2,400 (21.50%) |
| Mean random-intervention advantage | -0.553 |
| Positive maps | **20 / 20** |
| Positive opponents | **6 / 6** |
| Positive roles | **both** |
| Positive action planes | **10** |
| Largest positive-label map share | **8.62%** |
| New catastrophes | 5 / 2,400 |

All nine precommitted gates pass.  The result is not “local actions are good”: a uniformly sampled
alternative has negative mean value and is more often harmful than beneficial.  The result is
that positive exceptions are common and broad enough for a selector to have a learnable target.

## Structure of the signal

The signal is strongest in resource timing decisions.  `PICK` alternatives produced 245 positive
labels out of 865 (28.32%) and a +0.126 mean advantage.  `HARVEST` and `MINE` had high positive
rates (35.69% and 33.08%) but negative mean advantages, showing asymmetric downside and making a
precision-first guard necessary.  `CHOP` was close to neutral on average but positive in only
4.46% of samples.  `DROP` and `PLANT` positives were too sparse to support verb-only rules.

Positive labels were not an artifact of one opponent: rates ranged from 13.25% against
`legend_balanced` to 22.75% against `compact_gold`.  Both active-worker roles were represented
(248 and 181 positives).  The final turn quartile was less promising (9.80% positive) than the
first three (20.39%--22.65%), so turn context should be available to the distilled selector.

## Next experiment

Generate a larger corpus on map blocks disjoint from D16 and from one another.  Fit a compact
selector only from deployable state/action features, tune its abstention threshold on validation
maps, and open the locked test block once.  The model must optimize precision rather than raw
accuracy: `KEEP` remains the default, and an alternative is eligible only when the model predicts
a robust positive exception.  Only a successful held-out distillation gate may authorize an exact
full-trajectory policy evaluation.

## Evidence

- rows SHA-256:
  `a95bcf9e49dc7e7ea5dea9b02f7de144bdefc6d1de2cc49e9d1333eb1ed3431a`;
- analysis SHA-256:
  `b4101ee1ac918d99ec6352ae11dd1139644664dccbeb6d3f8540043ad06b6210`;
- teacher runner SHA-256:
  `1563e83e14b4a3538c1ecda7faa7ee9d2285bb9bf1363b1503c6869ca88f9850`;
- analyzer SHA-256:
  `d05f63a754804ebd3303a607e113480b35486599da000ad043730e83c7f5f204`.
