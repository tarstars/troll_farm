# D86a two-worker renewable role split — result (2026-07-21)

## Verdict

**Reject static opening selection and do not build the proposed yaichi imitation.**  The field
mechanism is genuine, frequent, and economically large, but the frozen opening-visible selector
does not transfer: held historical balanced accuracy is **0.583**, and its descriptive current
D61p accuracy is exactly chance (**0.500** balanced).  No resident or platform state changed.

## Exact evidence

All 25 frozen historical games and ten consumed current games decode exactly.  Twenty-process and
single-process extraction produce byte-identical rows.  Every trajectory length, unknown-update,
terminal score, terminal inventory, opening feature, seat, and historical-reference check passes;
fruit-provenance underflow is zero.

The strict label requires the starter to replant at least three fruit tokens that it harvested by
turn 100:

| Block | Games | Renewable | Nonrenewable |
|---|---:|---:|---:|
| historical discovery | 15 | 11 | 4 |
| historical validation | 10 | 6 | 4 |
| current D61p, consumed/descriptive | 10 | 6 | 4 |

This is not a cosmetic behavior.  On held historical validation, renewable games average 292.3
score, +120.5 margin, and 71.5 wood versus 137.3, -14.8, and 32.5 in nonrenewable games.  The
contrast is observational and map-confounded, so it cannot establish the treatment value.

## Selector failure

The frozen depth-two discovery tree used `fruit_total <= 19` and then
`own_nearest_tree_distance <= 2.5`.  It fit discovery at 0.909 balanced accuracy but failed the
untouched validation block:

| Measure | Required | Validation | Current descriptive |
|---|---:|---:|---:|
| balanced accuracy | >= 0.75 | **0.583** | 0.500 |
| renewable precision | >= 0.75 | **0.667** | 0.600 |
| renewable recall | >= 0.75 | **0.667** | 0.500 |
| nonrenewable recall | >= 0.60 | **0.500** | 0.500 |

Validation confusion is TP 4, TN 2, FP 2, FN 2.  A compact rule that looks excellent on 15 maps
does not identify the controller's decision on later maps.  This independently closes the static
first-move story even if the role definition is relaxed.

## Role-gate interpretation

The frozen role gate also fails: only 5/17 historical and 2/6 current renewable games exceed 80%
successful CHOP among the trained worker's productive non-MOVE actions.  This threshold measured
banking logistics, not role impurity.  In **all 17** historical renewable games, the trained
worker's only successful productive verbs are CHOP and DROP; its CHOP share ranges 68.5%--83.4%
because a carry-2 worker must repeatedly deposit wood.  The starter owns 100% of reinvested fruit.

Therefore the broad semantic observation survives—yaichi has a farmer and a wood-lifecycle
worker—but the preregistered numerical decomposition does not.  The failed gate is reported, not
retuned.  More importantly, correcting that definition would not repair the independent held-map
selector failure.

## Next eligible question

Static map selection is closed.  The remaining distinct hypothesis is action-local: after the
resident itself has already selected a non-orchard HARVEST, preserve that freshly observed species
as a regeneration commitment instead of banking it.  This avoids a map classifier and does not
add a worker or steal the secure mother's saturated harvest stream.  D87 must test that one-line
semantic bridge prospectively in complete closed-loop games; prior sparse-farm thresholds and
farmer assignment remain closed.

## Reproducibility

```text
4a11369733ac7361e08bb1ed563911a6b3a5f40f3e92d1f7ee00917825b889c7  d86a protocol
30b0f6e9c8db920bb7838514e358227364aca0bee0256639bd7acc34f15d96f4  analyzer
ebb6c99ba91afb881aa5f49f853e0c92302e69e9ebec814f113b769151dd3929  analyzer tests
8ebf4cd2f2f71849ba45ecdaf7d98fb68d74777462c20d1a7b8cc376bb509564  result JSON
64905dcda56e117d5ea173a60747e8db6fb1e2ef3311ef5a6de81bbca20cd65b  rows A
64905dcda56e117d5ea173a60747e8db6fb1e2ef3311ef5a6de81bbca20cd65b  rows B
```

Focused tests: 4 passed.
