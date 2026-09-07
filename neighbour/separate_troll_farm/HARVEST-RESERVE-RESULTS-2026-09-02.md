# V470 and V471, harvest power on the second troll with an apple reserve: neutral, closed — 2026-09-02 (loop iteration 4)

Queue item 1 after iteration 3: give the second troll harvest power the way the top three players
do (2/2/2/2), but only when the apple cost plus a reserve of one apple fits the stock, so that the
apple orchard's seed is never spent (V455/V456 lost 39 points by spending it). V470 allows harvest
power up to 2, V471 up to 1; everything else is V439. `build_v470_harvest_reserve.py`, development
panel of 8 maps and 192 paired games, `panel_gate.py` and `panel_diagnostics.py`.

| candidate | own score at 100 / 200 / 300 (baseline 85.0 / 169.2 / 238.5) | opponents' delta | wood (44.3) | harvests (63.3) | orchard plants in ring (5.2) | W/T/L (173/5/14) | gate |
|---|---|---|---|---|---|---|---|
| V470, harvest up to 2 | 83.1 / 166.3 / 235.3 | -1.2 | 43.7 | 63.5 | 5.2 | 170/3/19 | FAIL, -3.2 |
| V471, harvest up to 1 | 84.2 / 168.0 / 237.0 | -0.5 | 44.0 | 63.4 | 5.2 | 171/3/18 | FAIL, -1.5 |

## What the panel showed

The reserve does what it was meant to: the orchard is planted and harvested exactly as in the
baseline, and the second troll still trains at the median turn 12, now as 3/2/1/2 or 2/2/2/2
when the apples allow. But harvests per game do not move (63.4 against 63.3): in this bot the
starter does all the harvesting, saturated by the two-turn apple cycle, and the second troll only
chops, so its harvest power is never exercised. The loss is the two to five apples the talent
costs, worth one point each in the bank, and a little wood from the extra turns.

## Consequences

- Item closed. Harvest power on the second troll has no use in V439's division of labour; it
  would only pay together with a job that needs a second harvester, and none has passed.
- Together with V455 to V469 this completes the picture: fruit is not the gap, protecting trees
  costs points, target choice is worth about +3, and the second troll's 40 wood in 280 turns is the
  number to raise. The remaining lever in the queue is more chopping troll-turns: a third troll
  funded by mined iron.
