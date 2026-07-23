# Troll Farm — Bronze league (full rules)

Reached by beating the league-2 boss with bot v0.5.2. Bronze is the **final rules
league** ("no additional rules in higher leagues"). Parsed from `docs/plays/next_level.html`.

## What's new vs league 2
- **Terrain**: GRASS `.`, WATER `~`, ROCK `#`, IRON `+`, SHACK `0`/`1`. **Only GRASS is
  walkable** (water/rock/iron/shack are obstacles). The initial-map lines now contain these
  chars. (Bot fix v0.5.3: `parse_grid` now marks only `.` walkable.)
- **Water speeds trees**: a tree next to water has a much shorter cooldown.
  | type | cooldown | near water |
  |---|---|---|
  | PLUM | 8 | 3 |
  | LEMON | 8 | 3 |
  | APPLE | 9 | 2 |
  | BANANA | 6 | 4 |
  Tree health by size (matters for chopping): PLUM/LEMON 6/8/10/12, APPLE 11/14/17/20,
  BANANA 3/4/5/6 (size 1..4). A damaged tree that grows gains the size health-difference.

## New actions
- `CHOP id` — chop the tree on the troll's cell, reducing its health by `chopPower`. When
  health hits 0 the tree **disappears** and the troll collects **wood = tree size** (capped
  by free carryCapacity; overflow vanishes). Two trolls split wood one at a time; last wood
  can duplicate (like harvest).
- `MINE id` — a troll **adjacent to an IRON cell** mines, gaining up to `chopPower` iron
  (limited by free carryCapacity). Iron is infinite.

## Scoring (key strategic lever)
- Each fruit in the shack = **1 point**. Each **WOOD = 4 points** (`WOOD_POINTS=4`).
- So chopping a size-4 tree yields up to 4 wood = **16 points** — but destroys the tree
  (no more fruit from it). Wood is the big scoring multiplier in Bronze.

## Training (now 4 attributes)
- `TRAIN moveSpeed carryCapacity harvestPower chopPower`. Cost per attribute = `n + stat²`,
  paid from the matching resource: PLUM→moveSpeed, LEMON→carryCapacity, APPLE→harvestPower,
  **IRON→chopPower**. So chopPower trolls require mined iron.

## Boss observed (this replay)
Neither player chopped or mined; the boss is still essentially a fruit-gatherer (it won the
harvest count only because v0.5.3's predecessor was pathing-broken). So fixing walkability
(v0.5.3) likely makes us competitive on fruit alone — but to reliably win Bronze and beyond,
exploit **wood (4 pts via CHOP)**, **iron→chopPower training**, and **water-adjacent trees**.
