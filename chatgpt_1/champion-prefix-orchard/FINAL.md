# Champion-prefix orchard experiment — final result

Date: 2026-09-04  
Task: `20260904-champion-prefix-orchard`  
Artifact pin: `2fc4d285c391b66fc575ae2fec00d0957ea3c9e2`  
Verdict: **`DEAD_ON_NORMAL_PAIRED_REPLAY`**

## Answer

A small fixed near-shack orchard added after the unchanged champion's own second troll **does not beat the champion's continuation in this experiment**. The registered primary selector — leave one map out, choose one globally valid policy on the other 23 maps, then score it on the held-out map — selected **`NO_PLANT` in all 24 folds**. Therefore paired final margin and paired own score are both exactly **0.00**, with 95% bootstrap intervals **[0.00, 0.00]**.

This triggers the pre-registered dead condition that the paired final-margin lower bound must be above zero. The experiment stopped before high raid, panel, holdout, or ladder work.

## Integrity and mechanics

- The executable in both arms was the unchanged champion, SHA-256 `321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f`.
- All candidate streams were byte-identical to the champion through its own second `TRAIN`.
- The second troll's talent tuple and training turn were unchanged on every run.
- Third training was disabled; `NO_PLANT` was always legal.
- Baseline mechanics were clean on all 24 map-seats.
- Six instrument tests passed, including the planter self-occupancy regression.
- The corrected experiment evaluated 20 planting policies on 24 maps, plus 24 cached champion baselines: **504 complete 300-turn executions**.
- **17/20** planting policies were rejected because they introduced a new long-inactivity interval; this alarm is not called a loss or crash.

The first execution had a real instrument defect: when the planter reached its target, the target was rejected because it was occupied by the planter itself. That run planted zero trees and was discarded. The repair changed only that transition and added a test; policies and thresholds remained frozen. The artifact pin above is the corrected execution.

## Fixed-policy results

Only three planting policies survived the activity gate on every map. None had positive mean paired margin:

| fixed policy | Δ final margin, mean [95% CI] | Δ own score, mean [95% CI] | plants/game | fells/game |
|---|---:|---:|---:|---:|
| NO_PLANT | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 | 0.00 |
| BANANA-s85-k4-d4 | -3.38 [-10.17, 2.71] | 0.42 [-4.92, 5.79] | 3.62 | 1.79 |
| BANANA-s100-k4-d4 | -1.58 [-6.42, 2.75] | 0.38 [-4.25, 4.62] | 2.92 | 1.21 |
| APPLE-s70-k2-d2 | -6.12 [-12.96, 0.50] | -2.12 [-8.75, 4.58] | 1.79 | 1.17 |

The best planting policy by mean margin, `BANANA-s100-k4-d4`, still measured **−1.58** margin points per game. Its own-score mean was +0.38, but both intervals crossed zero and opponent score moved enough to make final margin negative. The in-sample global choice was therefore also `NO_PLANT`.

## Heterogeneity, and why it is not a rescue

A hindsight per-map oracle chose an orchard on **16/24** maps and `NO_PLANT` on **8/24**. Counts were:

```json
{
  "APPLE-s70-k2-d2": 5,
  "BANANA-s100-k4-d4": 2,
  "BANANA-s85-k4-d4": 9,
  "NO_PLANT": 8
}
```

That hindsight upper bound had paired margin mean **7.33**, 95% interval **[4.21, 11.08]**, and paired own-score mean **9.25**, interval **[5.62, 13.54]**. Map signs were `{'zero': 8, 'positive': 16}`.

This is descriptive only: it chooses after observing the exact final result on the same map. It demonstrates map-dependent opportunity, not a deployable selector. The registered leave-one-map-out rule could not predict those maps and correctly fell back to the champion. Building a map classifier now from the same 24 development maps would be post-result tuning and is outside this card.

The hindsight rows also do not pass the wood-calibration idea cleanly: predicted convertible wood totaled **94.46**, realized orchard wood **55.00**, and the row-wise 90th-percentile overstatement is `infinite` because some selected orchard plans predicted wood but banked none. This is another warning against treating the oracle upper bound as a policy.

## Interpretation

The positive kinetics result remains true: nearby mature banana wood is much faster to convert than distant wild wood. What failed is the stronger whole-game claim that a simple fixed orchard schedule captures enough of that advantage after paying its opportunity cost. The champion already uses those workers, cells, seeds, and opponent interactions; a locally attractive reserve often displaced more valuable continuation work.

The experiment also confirms that preserving the champion prefix repairs the architectural disease seen in the previous builds. The orchard result is not confounded by an altered second troll. It is simply not positive under a policy that generalizes across these development maps.

## Recommendation

**Close this orchard-optimizer line and do not give it a ladder slot.** Do not tune start turns, counts, inactivity thresholds, or a map selector on these 24 maps. Preserve the per-map heterogeneity as a clue for future strategic work, but a new orchard card would require a genuinely new, pre-specified map-conditioned signal and fresh development cases—not another sweep of this grid.

Per the task card, `claude_1` should now independently reproduce the measurement without reading this implementation. No ladder, platform, Arena, panel, holdout, cluster, champion, or `main` action was taken.

## Reproduction

```bash
bash chatgpt_1/champion-prefix-orchard/run.sh
```

Raw policy-by-map rows are in `results/result.json`; the frozen policy and action manifests are `policies.json` and `action-vocabulary.json`.
