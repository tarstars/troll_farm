# D2 builder brief — v1.43.0-yield (task-interference / yield-to-urgent)

**Origin:** user architecture request (2026-07-08): "picker stands on the banana tree, picking
fruits, and it blocks the way of the wood gatherer — solve it at the level of missions:
urgency, blocking." This is the L3→L2 feedback edge in the three-layer design.

**Base:** session-2026-07-01 HEAD at dispatch time (controller fills exact commit; includes
v1.41.0-nopickloop + v1.42.0-idlefruit). Worktree isolation. VERSION → "1.43.0-yield".

## Grounded engine facts (verified 2026-07-08, do not re-derive)

1. `rust/src/game/engine.rs::apply_moves` (:204-280): per-player resolution; `occupied`
   starts as ALL of that player's unit positions; a mover lands only on
   `!occupied.contains(cell)`; a STATIONARY unit never vacates → its cell is a hard wall for
   landings all turn. No exceptions (even `resolve_blocking` respects `occupied`).
2. BUT `next_cell(walkable, pos, dest, ms)` paths over terrain only → an ms≥2 mover can pass
   THROUGH a stationary teammate mid-path and land beyond it. `motion::solve_moves` already
   models exactly this (stationary cells excluded from LANDINGS only, :166/:199).
3. Swaps/chains among MOVING teammates are legal (solver comment :211-213 + crossing-swap
   test in tests/planner_solver.rs). So converting a blocker from stationary to mover is
   sufficient to unblock a 1-wide corridor via chain.
4. Turn priority: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE (engine.rs :691-693).
   A yielded harvester loses at most its harvest THIS turn; it can re-acquire next turn.

## Design (minimal, one yield round per turn)

After `planner::assign` produces assignments (with their VALUES) and intents, and after the
first `motion::solve_moves`:

1. **Detect:** for each mover M (has a MoveTo-style intent) whose chosen landing == its
   current cell (zero progress): for each stationary teammate S, test cheaply whether M's
   best-progress landing was excluded solely by S's cell (re-filter M's own candidate
   landings with S's cell allowed; no joint re-solve for detection). Collect (M, S) pairs.
2. **Policy (values, not band labels):** yield iff `value(M's assignment) > value(S's
   assignment)` (strict, on the already-computed i64 assignment values). Lower- or
   equal-value movers never displace a worker.
3. **Act:** suppress S's current candidate (that exact troll→target pair), re-match S ONLY
   (S's next-best candidate from the existing matrix — do NOT recompute other trolls'
   assignments; they are sticky/committed this turn). S now has a move-ish intent (its
   next-best target, or park). Re-run `solve_moves` once with the updated intent set.
4. **Bound:** at most ONE yield round per turn (no cascades). If S's re-match still leaves
   M blocked, accept — next turn re-detects. Flapping is bounded: S re-acquires its target
   the turn after M passes (sticky helps re-acquire, value 6 tiebreak).

Keep the whole thing behind the existing L2/L3 seam: a `yield_pass(state, my, plan,
assignments, intents) -> Option<updated intents>` helper in planner.rs or a small module —
match the file layout the code already uses. @TFMOVE-style one-line telemetry when a yield
fires (DEBUG-gated): `@TFYIELD t=<turn> blocker=<id> mover=<id>`.

## Tests (TDD; RED first, then implement)

1. `yield_corridor`: 1-wide corridor (copy fixture style from tests/pickloop.rs /
   motion_corridor.rs): picker S stationary-harvesting on a tree cell mid-corridor
   (idle-fruit band 38 or standing-harvest — pick whichever is constructible), chopper M
   behind it carrying wood, bank/shack beyond S; M's band 80 (full-bank) > S's. EXPECT: S's
   command is a MOVE off its cell (or the joint landing differs from S's cell) AND M's
   landing advances toward the bank. Pre-fix RED: M's landing == M's cell (blocked), S
   harvests.
2. `no_yield_when_blocker_outranks`: same geometry, but S is the higher-value task (e.g., S
   is the full-bank chopper standing on its bank-path cell doing endgame-bank 95 — or
   simplest: swap the values so value(S) > value(M)). EXPECT: no yield — S's command
   unchanged, M waits. Must pass pre- AND post-fix (regression pin, Test-B style).
3. `yield_single_round`: construct M blocked by S1 and S2 in sequence (or S's re-match also
   blocked): assert exactly one re-match attempt this turn (telemetry count or assignment
   diff), no infinite loop, deterministic output.
4. Full suite green (58 pass / 7 ignored baseline) + self-determinism equality 8 seeds +
   bundle/minify/compile gates + artifacts frozen per the standard builder procedure
   (docs/superpowers/plans/pipeline-briefs.md §builder).

## Risks / watchlist for gate

- Yield must NOT fire when M is blocked by ENEMY units or terrain (S detection is
  same-team stationary cells only — enemy positions are not in `stationary`; verify).
- Endgame liquidation traffic (band 95/80 convoys) is where yields will fire most — watch
  wood delta on the boss mini-gate (reference: wood ~51 on the boss pool, v1.41.0 gate #3).
- Sticky flap telemetry (@TFFARM flaps) should stay in the 2-12/game era band.
