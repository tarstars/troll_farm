# Motion solver — empirical findings & TDD plan (2026-07-06)

Goal: eliminate wasted troll moves (blocking near the camp) → more actions/turn → more wood → higher
rank. Approach (user's directive): discover the REAL engine's motion rules via experiments + logs,
fix them as local tests, then build the solver TDD-style. Do NOT assume rules — the sim may differ.

## The empirical harness (built, working)
- **Debug logging** (`main.rs`, DEBUG=true): `@TFMOVE t=<t> pos=[id@x,y ...] moves=[MOVE id x y ...]`
  logs our trolls' positions BEFORE moving + the intended MOVE targets each turn. Paired with the
  next turn's positions, this is (state, intents) → (result) for verifying move resolution.
- **`cgauto/motion_analyze.py`**: parses a collected game's stderr and reports observed motion facts
  (blocks, swaps, speed) + (TODO) diffs the sim's `apply_moves` prediction vs the real result.
- Collect a game: play the DEBUG bot via TestSession/play, dump `frames[].stderr` to a file, run the
  analyzer. (Play API is rate-limited — collect in small bursts.)

## VERIFIED against the real engine (game 895267080, 1 game so far — WIDEN THIS)
- **SPEED rule HOLDS:** a troll moves at most `ms` cells/turn toward its target (0 speed violations
  over 434 moves). Matches sim `next_cell` (up to `ms` along the shortest path).
- **SWAP rule CONFIRMED:** two adjacent trolls stepping toward each other exchange cells (4 observed).
  Matches sim `apply_moves` circular-swap resolution. → colliding≠blocking; a solver must exploit this.
- **BLOCKS = 4.1%** (18/434): a troll intended to MOVE but did not advance (contention) — the waste to
  kill. This is WITH v1.20.0's distinct-camp fix, so ~4% remains from path crossings / farther conflicts.

## Sim motion model (engine.rs — the hypothesis, now partly verified)
- `next_cell(walk, pos, target, ms)`: BFS; if target within `ms` go directly, else step `ms` cells
  along the shortest path toward it.
- `apply_moves`: per-player; movers sorted DESCENDING id (highest id wins a contested cell); a mover
  advances iff (only 1 wants the cell OR resolve_blocking) AND the cell is unoccupied; unresolved
  cycles SWAP; if still stuck, `resolve_blocking` forces the highest-id mover through.

## CORRIDOR UNLOAD — verified optimal + test-locked (user scenario 2026-07-06)
A 1-cell-wide corridor to the camp has only ONE drop cell, so "distribute to distinct camp cells"
(v1.20.0) can't help — it's pure sequencing. Verified (`src/bin/corridor.rs` + `tests/motion_corridor.rs`,
running the sim's real move rules): the simple policy **"full troll → drop-cell, JUST-EMPTIED troll →
exit"** unloads optimally via the SWAP rule — the empty troll heading out and the next full troll
heading in cross-step and swap, pipelining the single drop cell. **3 full trolls unload in 5 turns
(drop, swap, drop, swap, drop) — optimal; 2 trolls in 3.** Tests lock this (`cargo test --test
motion_corridor`). **Design rule for the solver: after a DROP, route the emptied troll OUTWARD (toward
the corridor mouth / its next task away from camp) whenever full trolls are queued behind it — never
let it wait/park in the corridor (that's the only way this blocks).** decide_elite mostly does this
(post-drop task is usually a tree out in the map) but the solver must GUARANTEE it.

## TDD plan (next)
1. **Widen verification:** collect ~10-20 games (incl. 2-troll camp congestion), extend the analyzer
   to reimplement `apply_moves` and DIFF its prediction vs the real transition. Any diff = a real rule
   the sim gets wrong → pin as a failing local test, fix the model.
2. **Fix rules as tests** in `tests/` (speed, contested-cell winner, swap, deadlock) using REAL cases.
3. **Build the solver** (TDD): given each troll's GOAL cell, choose MOVE targets so simulating
   `apply_moves` yields max progress (no blocks) — sidestep/sequence conflicts, exploit swaps. Verify
   the block rate drops toward 0 on the collected games.
4. **Integrate** into `decide_elite` (replace the reactive watchdog + per-troll bank/park cell picks),
   arena-validate vs the current best (v1.19.0/v1.20.0, rank ~118).

## v1.21.0 — proactive re-route + goal-directed sidestep (VERIFIED block-rate drop)
Two changes to decide_elite's motion tail (`main.rs`):
1. **Goal-directed watchdog sidestep** — when the anti-stall watchdog fires, sidestep to the free
   ortho-neighbor CLOSEST to the goal (min manhattan to target), not a random one. A random sidestep
   can waste the turn moving away.
2. **Proactive collision re-route** (before the watchdog) — a moving troll whose BFS next-step lands
   on a STATIONARY teammate (one doing CHOP/DROP/PLANT/MINE/WAIT this turn → no swap possible) will
   block. Re-route it THIS turn to a non-regressing free neighbor, resolving the waste immediately
   instead of after the 2-stuck-turn watchdog delay. Fires only on this clear stationary-block case,
   so it can't disrupt swaps.

**MEASURED (4 real Boss-5 games, 1674 moves):** BLOCKS **4.1% → 1.73%** (29/1674; per-game
0.7-2.9%) — a ~58% reduction. SWAPS still fire, SPEED violations 0, no runtime panic (300 turns
each), minified compiles (edition 2021). Submitted for arena validation vs v1.20.0 (@117, score
18.4). Note: collector now saves raw per-frame stderr to `game_<id>.raw` (the `.log` is only a
parsed summary) — run `motion_analyze.py` on the `.raw`. CAVEAT: all 4 games were still LOSSES
(43-63, 56-65, …) — motion cuts waste but does NOT close the economy gap; see the late-throughput
ceiling ([[late-throughput-ceiling]] memory): we lead early, Boss out-produces 2× late with
identical cc2 builds because our single starter can't refill the tight farm → chopper starves.

## Status
- v1.21.0 submitted (block 4.1%→1.3% verified), converging. Fallbacks: v1.20.0 (@117), v1.19.0 (@118).
- Motion is a real but MODEST lever; we still lose ~50-55 wood games to Boss-5's economy. The next
  lever for rank <100 is the seed/production economy (per the ceiling analysis), not more motion.
