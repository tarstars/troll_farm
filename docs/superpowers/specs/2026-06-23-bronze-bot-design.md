# League-2 (Bronze / "Wood 1") bot — design

Date: 2026-06-23. Status: approved (pre-implementation).

## Goal
An "aggressive optimizer" bot for league 2, which unlocks TRAIN / PLANT / PICK and runs
300 turns. We build a **fast deterministic live heuristic** that does multi-troll
gathering + a training economy + planting, and a **faithful offline simulator + harness**
used to playtest against the league-2 boss and tune the heuristic's parameters. No live
game-tree search (kept comfortably under the 50 ms/turn budget).

See `docs/statement_bronze.md` and `docs/mechanics.md` for the verified rules this relies
on (training cost `n + stat²`, harvest rounds + last-fruit duplication, per-player move
resolution, plant/pick effects, score = banked fruit, etc.).

## Decisions (from brainstorming)
- **Ambition:** aggressive optimizer.
- **Engine:** strong heuristic tuned by an offline simulator (sim not used live).
- **Planting:** included in v1 (gated behind tunable params; tuner may drive it to ~0).
- **Code sharing (Approach A):** `bot/main.py` is the single-file submission *and* the
  shared library; dev-only tools import mechanics from it. No bundler, one source of truth.

## Architecture / module layout
- `bot/main.py` — the submission and shared library:
  - Data model: `Troll` (id, x, y, movementSpeed, carryCapacity, harvestPower, per-type
    carry + total), `Tree` (type, x, y, size, health, fruits, cooldown), `State` (walkable
    set, my_shack, opp_shack, my_inventory, opp_inventory, trees, my_trolls, opp_trolls,
    turn).
  - Pure mechanics: `bfs_distances`, `predict_fruits`, training-cost, plant/pick helpers.
  - Heuristic: `decide(state, params) -> list[str]`.
  - Tunable `PARAMS` dict (baked-in defaults).
  - stdin/stdout game loop under `if __name__ == "__main__"`.
- `sim/` (dev-only, not submitted; imports mechanics from `bot.main`):
  - `sim.py` — faithful referee step.
  - `mapgen.py` — port of league-2 `Board.createMap` (symmetric shacks, trees with mirror +
    random aging, validity checks). Seedable.
  - `boss.py` — Python port of `config/level2/Boss.cs`.
  - `harness.py` — play bot vs boss over N seeded maps → win-rate + mean score margin; CLI.
  - tuner — coordinate-ascent / small grid search over `PARAMS`.
- `tests/` — unit + behavior + sim + one end-to-end stdio test.

## Live decision flow (`decide`, per turn)
1. Precompute BFS fields: one from each troll's position; one "return" field from the
   shack's walkable orthogonal neighbours (distance to a drop position).
2. **Gather with reservations.** Assign each empty/partial troll the best *unreserved* tree
   by round-trip cost `walk + wait_to_ripen + return`; reserve its predicted fruit so two
   trolls never chase the same fruit. Generalized for `carryCapacity > 1`: a troll keeps
   topping up across nearby trees until full, or until the marginal round-trip value drops
   below a tunable threshold, then banks. Per-turn action: `HARVEST` when on a fruited tree
   (opportunistic if not full); `MOVE` toward target; `MOVE` to shack then `DROP` when
   adjacent and banking; `WAIT` to camp a not-yet-ripe target.
3. **Training (economic).** While the shack cell is free, we can afford a target spec, and
   `turns_left > payback`, emit one `TRAIN m c h 0`. A `score_reserve` keeps banked fruit
   ahead of the opponent. (Only one train/turn; a freshly spawned troll must vacate the
   shack before the next.)
4. **Planting (orchard role).** When near the shack, `PICK` a seed (costs banked fruit),
   carry it to the nearest empty grass cell, `PLANT`. Prefer fast types (BANANA, cd 6).
   Gated by tunable plant budget / target-cell count.
5. Emit one command per troll (+ optional `TRAIN`, + `MSG`), `;`-joined.

## Training economy (core knob)
Exact cost `n + stat²` per resource (PLUM↔movementSpeed, LEMON↔carryCapacity,
APPLE↔harvestPower; `harvestPower ≤ 3`, `chopPower` must be 0 in league 2). Tunables:
`max_trolls`, candidate `train_spec(s)`, `min_turns_left_to_train`, `score_reserve`. The
harness searches these to maximize win-rate then score margin. Bananas are never a training
cost, so the reserve protects pure-score fruit.

## Simulator faithfulness
`sim.py` parses both players' command strings and applies tasks in referee priority order
(MOVE 1 → HARVEST 2 → PLANT 3 → PICK 5 → TRAIN 6 → DROP 7), then ticks plants and recomputes
scores. It reproduces: harvest rounds with last-fruit duplication; per-player move conflict
resolution (highest-id-wins contested cell, circular swaps, random tie-break among equal
next-cells); TRAIN blocked when the shack cell is occupied; PLANT same-type vs contradicting
resolution. Cross-checked against referee facts — e.g. the statement example (2 trolls,
`TRAIN 2 3 1 0` → 6 PLUM / 11 LEMON / 3 APPLE) and the existing `predict_fruits` cases.

## Offline harness & tuning
`harness.py --games N --seed S` plays bot vs boss across N seeded maps; reports win-rate and
mean score margin, with optional per-game logs. Tuning: start from hand-set `PARAMS`, then
coordinate-ascent / small grid over the key knobs, maximizing win-rate then margin. Best
`PARAMS` are written back as `bot/main.py` defaults.

## Testing strategy (TDD)
Test-first for every new unit:
- Mechanics: `bfs_distances`, `predict_fruits`, training-cost, plant/pick.
- `decide` behaviors: no double-booking, capacity-filling across trees, banking threshold,
  training triggers/affordability, planting.
- Sim step: priority order, harvest duplication, move conflicts/swaps, train spawn + block.
- One end-to-end stdio test running `bot/main.py` as a process on a scripted game.

## Build order
1. Refactor model + parsing to multi-troll (`State` with lists, per-type carry).
2. Generalized gather + reservation assignment (we start with one troll; multi-troll
   support is for after training and for reading the boss's trolls). Checkpoint: a correct
   multi-troll gatherer — it may need step 3 (training a second troll) to reliably beat the
   boss's two trolls, but it is a submittable improvement.
3. Training economy.
4. Simulator + boss port + mapgen + harness (enables playtesting/tuning).
5. Tune `PARAMS` via the harness.
6. Planting, then re-tune and finalize.

Note: steps 2–3 are validated by unit tests before the sim exists; playtesting vs the boss
begins at step 4. If measure-first is preferred, step 4 can move earlier.

## Out of scope (YAGNI for now)
- Live lookahead / search. Chopping, mining, iron, water, rivers (league 3+). Map sizes >
  8×16 (height up to 11 only in later leagues).
