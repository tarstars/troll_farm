# Troll Farm — League 2 ("Wood 1" / TRAIN+PLANT), verified from referee

Unlocks over Wood: **TRAIN, PLANT, PICK**. Objective per welcome: use TRAIN and
control multiple trolls. Input/output line formats are unchanged from Wood — there are
just multiple trolls now. Still no water/rock/iron terrain (those are league 3+).

## What changed vs Wood
- **Game length: 300 turns** (was 100). Map still `height=8, width=16` (league <=2).
- **Starting inventory**: each of PLUM, LEMON, APPLE, BANANA = random **2..10**
  (IRON=0, WOOD=0). So you begin with capital and can TRAIN on turn 1.
- **Score is still your shack inventory**: PLUM+LEMON+APPLE+BANANA (+4*WOOD, irrelevant).
  Training SPENDS banked PLUM/LEMON/APPLE — i.e. it spends current score for future
  throughput. **BANANA is never a training cost → pure score.**

## New commands
- `TRAIN moveSpeed carryCapacity harvestPower chopPower`
  - Spawns a troll **on your shack cell** with those fixed stats. `chopPower` must be 0 here.
  - Validation: `moveSpeed`∈[1, w*h], `carryCapacity`∈[0,1000], `harvestPower`∈[0,3].
  - **Cost** (paid from shack inventory): with `n` = your current troll count,
    PLUM = `n + moveSpeed²`, LEMON = `n + carryCapacity²`, APPLE = `n + harvestPower²`.
  - **Blocked if a troll occupies the shack cell** → effectively one TRAIN/turn, and a
    just-spawned troll must move off before you can train the next.
- `PLANT id type` — on the troll's GRASS cell (no existing plant), consumes 1 carried
  fruit of `type`, creating a new **size-0** tree of that type. Same-type concurrent plant
  on one cell: both pay a seed, one tree appears. Different types: nothing happens.
- `PICK id type` — when next to the shack, move 1 of `type` from shack inventory into the
  troll's carry (spends score). For carrying a seed out to PLANT elsewhere.

## Turn apply order (task priority, ascending)
MOVE(1) → HARVEST(2) → PLANT(3) → PICK(5) → TRAIN(6) → DROP(7), then plants tick.

## Multi-troll mechanics (recap, see mechanics.md)
- A cell holds **≤1 troll per team**; your trolls can't stack (move conflicts resolved
  per-player, highest id wins a contested cell). Enemy units may share your cell.
- New stats matter: `carryCapacity>1` lets one troll fill across multiple trees before
  banking; `harvestPower` up to 3 empties a 3-fruit tree in one HARVEST.

## League-2 boss (config/level2/Boss.cs)
- Trains exactly **one** extra troll (`TRAIN 1 1 1 0`), capping at 2 weak 1/1/1 trolls.
- Same Manhattan greedy + quirky "farthest-of-nearest" tie-break, **no ripeness**.
- Due to a bug (`hasPlanted` never set true) it PLANTs a fruit whenever a troll returns
  full onto a tree-less cell adjacent to base — so it scatters a few slow size-0 trees by
  its shack and otherwise gathers with 2 trolls.
- Beatable by: more/better-statted trolls, BFS routing, ripeness prediction, and
  multi-fruit trips (carryCapacity).

## Bot work implied
- `parse_turn` must collect **all** our trolls (currently keeps only one).
- Decide commands for every troll + an optional TRAIN, avoiding double-booking trees and
  the shack bottleneck (DROP/TRAIN/spawn all contend for shack-adjacent cells).
- Generalize the gather loop for `carryCapacity>1` / `harvestPower>1`.
