# Goal-keeping ladder cost: stopped at the charter's dead condition

Task: `20260827-goal-keeping-ladder-cost`. Read-only result, 2026-08-27.

## Verdict

**UNDER-DETERMINED; stop under the charter's dead condition.** The supplied deterministic slice
has 208 champion games but only **four** keep-rule games. All four keep-rule games are losses by at
least 50 points (mean margin **−222.5**), so there is no keep-rule win group and no like-for-like
win/loss split. Those four games cannot explain a three-point ladder gap or distinguish the
owner's robustness hypothesis from opponent mix, map mix, seat mix, or ordinary sampling noise.

The available diagnostics also do not encode the three facts the hypothesis needs: why a goal
became invalid (opponent took the tree, occupied the cell, or removed the plant), the outcome of a
contested-tree episode, or score composition by resource and time. Inferring any of these from
goal text would turn absence of an instrument into a causal claim.

## What the four games do say

One script decoded every manifest-pinned replay with zero missing or hash-mismatched files:
`codex_1/analytics/goal_keeping_ladder_cost.py`. Its complete result is
`codex_1/analytics/goal-keeping-ladder-cost-2026-08-27.json`; the manifest SHA-256 is
`dacd2e6ebfbc11a68ce37b291bee6441076a19fbd37e9fc52378151f59212653`.

| measure | champion + v6 | keep rule + v6 |
|---|---:|---:|
| games / decoded turns | 208 / 56,288 | **4 / 1,200** |
| wins / losses / losses by ≥50 | 111 / 97 / 49 | **0 / 4 / 4** |
| mean own score / margin | 188.39 / +2.66 | 231.25 / **−222.50** |
| goal runs: count / mean / median / max turns | 18,989 / 3.21 / 2 / 21 | 375 / 3.67 / 2 / 21 |
| move share of unit commands | 51.23% | 47.13% |
| work share of unit commands | 44.00% | 48.81% |
| A→B→A reversals per 100 moves | 11.95 | 16.10 |
| unit-turns with keep active | inapplicable (0) | 1,003 |

The reversal point estimate is higher under keep (**16.10 vs 11.95 per 100 moves**), which is
directionally compatible with rigidity, but four games are not a population comparison. The goal
lifetimes are not substantially separated in this slice (median 2 in both; maximum 21 in both),
and version-6 `ka` never exceeds 20 in these four games. This slice therefore contains no example
of the long-goal failure the ticket is meant to price.

Within the champion's much larger arm, bad losses have more walking and less working than wins:
MOVE is **55.21%** of commands in 49 bad losses versus **50.34%** in 111 wins; work is **41.63%**
versus **44.62%**. That establishes that walking-versus-working covaries with outcomes for the
champion. It does not establish that keeping a goal causes the shift.

## Answer to the owner's hypothesis

The hypothesis is **under-determined**, neither supported nor refuted. What would settle it is a
balanced new slice with at least tens of keep-rule games including wins and ordinary losses, plus
telemetry that records goal termination reason, contested-target outcome, and per-resource score
deltas. The clean comparison is then stratified by map/opponent/seat and outcome; without those
fields, more games can estimate movement and work rates but still cannot test opponent-caused
invalidation directly.

## Exact reproduction

```text
python3 codex_1/analytics/goal_keeping_ladder_cost.py \
  --manifest data/raw/slice/manifest.json \
  --games-dir data/raw/slice/games \
  --output codex_1/analytics/goal-keeping-ladder-cost-2026-08-27.json
```

Definitions: a goal run is a maximal consecutive run of the same non-`NONE` chosen-goal string
for one unit. A reversal is a unit's move destination returning to its destination two MOVE
commands earlier (A→B→A). “Work” is HARVEST, CHOP, PLANT, PICK, DROP, or TRAIN. These are command
descriptions, not claims about successful referee effects.
