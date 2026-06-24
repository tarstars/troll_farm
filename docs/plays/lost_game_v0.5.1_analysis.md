# Lost game analysis — v0.5.1 (from docs/plays/lost_game.html)

Parsed from the replay DOM dump (our stdout per turn + game summaries). 300 turns.
Confirmed build via `MSG v0.5.1` on turn 1.

## Our command tally (across all troll-turns)
MOVE 292, WAIT 195, HARVEST 56, DROP 55, TRAIN 1, MSG 1. PLANT/PICK = 0.
We controlled only troll ids {0, 3} the whole game (2 trolls).

## Root findings
1. **Troll 3 was deadlocked.** It emitted `MOVE 3 2 7` on 276 of its 291 move-turns and
   never harvested/dropped — effectively a wasted troll for ~the whole game. Likely the
   collision resolver (`resolve_moves`/`landing_cell`) wedges a troll: when its only
   distance-reducing cell is claimed by the other troll every turn, landing_cell returns
   "stay", and it never re-routes. We can't confirm without per-turn positions (not in the
   replay's output stream) — needs the simulator.
2. **Stuck at 2 trolls (APPLE-starved).** Trained once (`TRAIN 1 1 1 0`, turn 2), never
   again. Training needs APPLE for harvestPower, and only **1 APPLE was harvested all game**
   by either player. APPLE scarcity hard-caps troll count. (Harvested by type, both players:
   PLUM 61, BANANA 56, LEMON 32, APPLE 1.)
3. **~195 idle WAIT turns.** The one working troll over-camps slow trees (banana cd 6):
   harvest 1 fruit, then idle for regrow instead of servicing another tree. Throughput was
   ~56 fruits over 300 turns.
4. Planting was NOT the problem on v0.5.1 — we planted 0; the boss planted 2.

## Implications for Plan 2 (simulator + harness)
- Need full per-turn state (positions, inventory) to debug the troll-3 deadlock.
- Tuning targets: (a) collision/anti-deadlock so trained trolls actually leave the shack
  and re-route; (b) anti-camping (don't WAIT on an unripe tree if other fruit is reachable);
  (c) training economy that copes with type scarcity (esp. APPLE) — pick affordable specs
  from current inventory, and/or target PLUM/LEMON/APPLE trees to fund growth.
