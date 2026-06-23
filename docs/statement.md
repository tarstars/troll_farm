# Troll Farm — CodinGame Spring Challenge 2026

> Source: https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm
> Parsed from `docs/troll_farm_dom_dump.html` on 2026-06-23.
> **Current league: Wood 4** (tutorial). Full rules unlock in Bronze.
> Referee source code: https://github.com/eulerscheZahl/Troll-Farm

## The Goal
Control a pack of trolls. Make them collect the most resources (fruits).

## Rules
Each player starts with a **shack** and a **troll**. Control your troll to collect
fruits and bring resources back to your shack. Resources can be used to train more
trolls or plant trees. The game is played on a grid; cells have different terrains and
trees on them.

### Troll attributes (fixed, can't change)
- `movementSpeed` — cells it can MOVE (horiz/vert) per turn
- `carryCapacity`
- `harvestPower`
- `chopPower`

### Trees
A tree has: `type` (PLUM, LEMON, APPLE, BANANA), `size`, `health`, `fruits`, `cooldown`.
- When `cooldown` reaches 0, the tree **grows in size**, or if at max size (4),
  **produces fruits**.
- Trees hold up to **3 fruits**.

### Moving units
- `movementSpeed` = how many cells a troll can MOVE horizontally or vertically per turn.
- Each cell holds at most **1 troll per team**.
- Only **GRASS** cells are walkable.
- The shack is also the spawn point, but trolls **can't walk back onto that cell**
  after leaving it.
- If the target is out of range or not walkable, the troll moves to the nearest
  reachable cell towards it.

### Harvesting
- Trees can be harvested if they have fruits.
- When a troll shares a cell with a tree, `HARVEST` takes as many fruits as possible,
  limited by free `carryCapacity` and `harvestPower`.
- Two trolls harvesting the same tree in parallel take one fruit at a time while fruits
  remain and they can still harvest. The **last fruit can be duplicated** so both trolls
  get it.

### Dropping items
- When a troll carrying resources is **next to its shack** (horizontally or vertically),
  `DROP` transfers all carried items to the shack.

## Victory Conditions
- Score more points than your opponent. **Each fruit in your shack scores 1 point.**

## Loss Conditions
- Fewer points than the opponent.
- Fail to respond in time or output an unrecognized command.

## Game Input

### Initial input
- **First line**: `width height` — the grid size.
- **Next `height` lines**: each line has `width` characters. In this league:
  - `.` = GRASS
  - `0` = your own SHACK
  - `1` = opponent's SHACK

### Input for each game turn
- **First two lines**: your inventory, then opponent's inventory:
  `plums lemons apples bananas (reserved) (reserved)`.
  In this league the last two values are always `0`.
- **Next line**: `treeCount`.
- **Next `treeCount` lines**: `type x y size health fruits cooldown`
  (`type` ∈ PLUM, LEMON, APPLE, BANANA).
- **Next line**: `trollsCount`.
- **Next `trollsCount` lines**:
  `id player x y movementSpeed carryCapacity harvestPower (reserved) carryPlum carryLemon carryApple carryBanana (reserved) (reserved)`.
  `player` = `0` if you own the troll, `1` otherwise.

### Output for one game turn
Print any number of commands separated by `;`:
- `MOVE id x y` — move troll `id` toward cell (x, y).
- `HARVEST id` — make troll `id` harvest on its current cell.
- `DROP id` — make troll `id` drop all carried items at the shack.
- `WAIT` — do nothing.
- `MSG text` — display a message in the replay.

## Constraints
- Response time first turn ≤ **1000 ms**.
- Response time per turn ≤ **50 ms**.
  (You only lose on time if you exceed the limit 3× by at most 50 ms, or once by more.)
- Game ends after **100 turns** (later leagues: 300).
- `height` = **8** (later up to 11).
- `width` = **2 * height**.
