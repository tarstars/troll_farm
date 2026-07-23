# D89a banana seed-factory — prospective discovery result (2026-07-21)

## Verdict

Reject the exact D89a controller on the frozen safety rule and keep confirmation maps
`9,914,048--9,914,063` sealed. The seed-factory architecture is strongly productive and remains
the leading branch, but this full-rate controller is not a submission candidate.

The one-worker and 20-worker executions over maps `9,914,032--9,914,047`, both seats, and all eight
opponents are byte-identical (`358160eaf53b31fb53e50fb2f3db5a5e109f84aa5fc042e8447acf3be5f630ab`).
All 512 rows, 256 resident/candidate pairs, provenance checks, shadow checks, worker-count checks,
and command-role checks pass. The analyzed result is
`d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a`.

## Mechanism result

The controller activates in 256/256 tasks, both seats, and all eight opponent families. It plants
all 1,344 initial bank BANANAs successfully. Exactly 192/256 tasks have a bank budget of at least
three, meeting the frozen 75% bootstrap gate. It reaches a sustained own-harvest/replant loop in
252/256 tasks, with 10,729 successful tracked-crop harvests and 10,611 successful renewable
plants. There are zero preactivation shadow mismatches and zero trained-worker forbidden commands.

This is the first local resident-derived controller in the current cycle to reproduce the complete
renewable mechanism at broad support. It adds, per task:

- `+162.305` own score;
- `+40.590` terminal wood;
- `+35.688` successful plants; and
- `+36.176` harvested fruits from owned crops.

## Value and safety result

Mean paired margin improves by `+79.441`; 179 tasks improve and 77 regress. The map-cluster normal
95% interval is `[+40.991, +117.892]`. Catastrophes fall from 26 to 11 and negative-margin mass
falls from 5,333 to 3,112 (`0.584x`). These are large, real gains.

Four preregistered safety gates nevertheless fail:

| Gate | Required | Observed |
|---|---:|---:|
| Worst opponent-family mean | `>= -5` | Gold adaptive `-6.938` |
| Active p10 margin delta | `>= -20` | `-72` |
| Active worst margin delta | `>= -60` | `-235` |
| Mean opponent-score delta | `<= +1` | `+82.863` |

The worst cell is map `9,914,047`, seat 0, against Gold adaptive: own score rises by 163 but the
opponent rises by 398, moving margin from `+133` to `-102` (`-235` delta). This is not a failed
factory: it bootstraps 2/2 seeds and completes 50 harvest/replant cycles.

## Causal decomposition

Direct theft of D89 crops is not the dominant leak. The candidate gives the opponent an average
score-equivalent `+12.453` through crops attributed to us. The much larger term is `+76.508` from
the opponent's own created crops (`+16.461` wood and `+10.680` fruit). Thus the factory changes the
competitive schedule: while the starter maintains private production, opponents—especially Gold
adaptive—complete more of their own reproductive loop.

For our side the corresponding shift is deliberate: acquisition from owned crops adds a
score-equivalent `+316.254`, while natural and opponent-created sources fall by `117.508` combined.
D89 proves private renewable conversion, but it spends too much starter attention on every tracked
descendant and relinquishes too much rival-loop pressure in the losing tail.

## Next eligible experiment

D90 will test the lineage boundary revealed directly by D88: bank-seeded crops produced 350/363
harvested fruits, while only 4/358 harvested descendants came from harvested-fruit plantings and
317 descendants were chopped by yaichi. On the consumed D89 maps, compare the full controller with
a source-separated controller that harvests only bank-seeded reproductive crops (or a promoted
reserve if all bank sources disappear). Renewable descendants remain conversion stock for the wood
worker and are never ordinary harvest targets.

This is one causal ablation, not a threshold or map selector. If it restores opponent pressure and
tail safety while retaining material production, freeze one D90 controller on new official maps.
Do not open D89 confirmation, submit, replace the resident, or use Arena from this result.
