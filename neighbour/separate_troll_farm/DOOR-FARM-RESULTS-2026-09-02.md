# V459 to V463, multi-slot door farm: measured and rejected — 2026-09-02 (loop iteration 1)

Queue item 1 of `RESEARCH-QUEUE.md`: replace V439's one-entrance banana farm with several door
slots so that trees grow in parallel, on top of V457's grow-before-fell protection. Built by
`build_v459_door_farm.py`; 8-map development panel against V439 (192 paired games each); gate
`panel_gate.py`, mechanism `panel_diagnostics.py`. Panels under
`/data/separate_troll_farm-working/panels/2026-09-02/`.

| candidate | slots and rule | own score at 100 / 200 / 300 (baseline 85.0 / 169.2 / 238.5) | wood (baseline 44.3) | WAIT per game (baseline 16.6) | W/T/L (baseline 173/5/14) | gate |
|---|---|---|---|---|---|---|
| V459 | cap 3, one door kept free, fell after 3 fruits | 85.3 / 166.8 / 235.1 | 42.7 | 70 | 164/2/26 | FAIL, -3.4 |
| V460 | as V459, fell after 1 fruit | 85.3 / 166.8 / 235.1 | 42.7 | 70 | 164/2/26 | FAIL, -3.4 |
| V461 | cap 3, all doors, fell after 1 fruit | 85.3 / 167.0 / 235.3 | 42.7 | 70 | 164/2/26 | FAIL, -3.2 |
| V462 | V461 plus adoption of regeneration-planted trees, any troll picks seeds | 81.0 / 149.1 / 211.4 | 36.6 | 131 | 151/0/41 | FAIL, -27.0 |
| V463 | as V462, fell after 3 fruits | 80.9 / 149.1 / 211.1 | 36.6 | 131 | 152/0/40 | FAIL, -27.4 |

## What the panels and one game trace showed

**V459 to V461 never engaged the new farm.** Their numbers are identical to each other and to
V457, and the ring never held more than 1.2 bananas at once, as in the baseline. The reason is
that V439 does not plant seeds through the farm layer at all: `PICK BANANA` registers a
"regeneration commitment" and the planner's endgame candidates plant the carried fruit on the
nearest empty cell. The farm's own planting trigger (a banana carrier arriving on an empty door)
almost never fires, which is also why V439's entrance farm "activated in five games" in the
README's history. Fixing the cap arithmetic (V461) changed nothing for the same reason.

**V462/V463 engaged it, and that was worse.** Adopting the regeneration-planted door trees as
slots and protecting them until their fruit target raised the ring's bananas to 1.7 but pushed
waits to 131 a game, chops in the ring from 61 to 40, wood from 44 to 37, and opponents gained 12.

**The trace (map 9941003, seat 1, V461 against legend_v7, own score 308 baseline against 232).**
The baseline runs its late economy as a conversion loop: from turn 110 the starter picks a banana,
plants it, fells the sapling at size 1 about five turns later, and repeats every six turns until
the banana stock runs out (six cycles in thirty turns, one wood each), then again after each
harvest of a natural banana. It waits five turns in the whole game. The candidate plants at turns
53, 71, 80, 94 and 103, then waits 59 turns, mostly right after each planting, because the
protected sapling is the only tree left near the shack; the trees do not survive to size 4 (the
opponent, or our own enemy-approach rule, fells them), the loop stops when the stock is spent, and
wood ends 20 lower. Every design in this family removes the baseline's only late income without
redeploying the freed troll time, and on these maps there is nothing to redeploy it to.

## What this says about the economy gap

Late in these games wood comes from planted trees, and the binding constraints are seeds and
troll time, not cells: the baseline's loop is limited by its banana stock, which is refilled only
by harvesting natural bananas. Growing a tree to size 4 for four wood pays 4x per seed but takes
24 turns on a plain cell (16 next to water) and needs the tree to survive; the loop pays 1 wood
per seed every six turns and needs nothing. The top players get both: mature trees that also
return three seeds per cycle. The sustainable form of that here is a small number of permanently
protected, water-adjacent mother bananas whose fruit feeds continuous conversions by both trolls,
not slots that pause the loop.

## Consequences

1. Item 1 (parallel door slots on top of grow-before-fell) is closed. The slot machinery
   (`build_v459_door_farm.py`) is kept because its protection set, arrival replacement and fruit
   accounting are what the mother-tree design needs.
2. New item 1: seed supply for the conversion loop (V464/V465): one or two mother bananas on
   water-adjacent door cells, planted by the farm on arrival or adopted, protected until turn 270,
   harvested by any arriving troll with harvest power and by the planner's existing nearest-banana
   harvest; every other sapling is fair game as in V439; any troll may pick a seed; loop from turn
   40. Judge by PICK/PLANT counts, wood and the gate.
3. The gate and diagnostics did their job again: five candidates measured and explained in one
   iteration.
