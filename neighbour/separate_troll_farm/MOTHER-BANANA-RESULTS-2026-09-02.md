# V464 to V467, mother bananas feeding the conversion loop: measured and rejected — 2026-09-02 (loop iteration 2)

Queue item 1 after iteration 1: keep V439's late-game conversion loop (pick a banana, plant it,
fell the sapling at size 1) and feed it seeds from one or two permanently protected mother bananas
on water-adjacent door cells. Built by `build_v464_mother_bananas.py` on the V459 machinery;
8-map development panel against V439, 192 paired games each; `panel_gate.py` and
`panel_diagnostics.py`. Panels under `/data/separate_troll_farm-working/panels/2026-09-02/`.

| candidate | mothers | protection | own score at 100 / 200 / 300 (baseline 85.0 / 169.2 / 238.5) | wood (44.3) | WAIT/game (16.6) | PICK/game (11.2) | HARVEST/game (63.3) | gate |
|---|---|---|---|---|---|---|---|---|
| V464 | 1 | drops every candidate on the mother's cell | 83.9 / 160.0 / 230.5 | 42.0 | 71 | 10.6 | 64.1 | FAIL, -7.9 |
| V465 | 2 | same | 82.8 / 155.8 / 226.4 | 40.8 | 89 | 10.0 | 64.3 | FAIL, -12.1 |
| V466 | 1 | drops chops only; harvests and harvest trips pass | 83.8 / 159.2 / 230.6 | 42.0 | 72 | 10.8 | 64.4 | FAIL, -7.8 |
| V467 | 2 | same | 82.8 / 155.8 / 226.5 | 40.8 | 86 | 10.3 | 64.7 | FAIL, -12.0 |

## What the panels and a trace showed

**Seed supply did not change.** Picks and harvests per game stayed at the baseline's level in all
four variants, so the mothers produced no seeds that reached the loop; the harvest-aware protection
(V466/V467), which lets the starter's HARVEST and approach through, changed nothing measurable, so
the filtered harvest was not the limiting step either.

**The trace (map 9941005, seat 0, V466 against the resident).** The baseline's economy on this map
is the apple engine: PLANT APPLE at turn 10 on a water door, then the starter harvests one apple
every two turns from turn 20 to the end (60 harvests, one point each), while the second troll chops
(wood 25). The candidate is identical until turn 108, when the second troll, now allowed to pick,
takes a banana and plants it on the water door; the tree is adopted as a mother and protected, and
from then on the second troll waits, 118 waits against the baseline's 31. Nobody harvests the
mother: the starter is fully occupied by the two-turn apple cycle, which is worth more than a
banana every four turns, and the second troll has no harvest power (2/2/0/2). Two mothers (V465,
V467) occupy two doors and idle the troll sooner, hence the larger loss.

## What this says

1. Fruit is not where the gap is, and the starter's harvest capacity is already spent on the
   apple engine. Any design that adds harvesting work needs a second harvester, which costs apples
   the engine needs (V455/V456), unless an apple reserve is kept (queue item on the harvest talent).
2. Wood on these maps is the second troll's chopping, about 40 wood in 280 turns, one wood every
   seven turns. Doubling it needs either more chopping troll-turns (a third troll, which the top
   players fund by mining iron around turn 100; V439 mines 0.25 iron a game) or more wood per chop
   trip (tree choice and the denial bonus that sends choppers to 20-health apples near the enemy).
3. Protecting any own tree from the planner has now cost points in every variant (V455 to V467),
   because the trolls have no alternative work near the shack. Protection is not the lever.

## Consequences

- Item 1 (mother bananas) is closed with items V455 to V463 as the same lesson from a different
  side: the farm-side changes do not raise wood on this bot.
- Next item: chop-target efficiency and the denial bonus, a one-line-at-a-time change in the
  planner's scoring, measured by wood per game and the gate; then the harvest talent with an
  apple reserve; then a mined-iron third troll.
