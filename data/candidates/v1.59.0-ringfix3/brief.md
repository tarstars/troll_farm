# v1.59.0-ringfix3 builder brief — FIX3 (banana no-carry-in-advance) ISOLATED on ringfarm

**Base:** v1.56.0-ringfarm = the CHAMPION (arena +1.7 @ 117/18.4, ~18% Boss 5, the only positive
economy result ever). Current session HEAD (VERSION 1.56.0-ringfarm). Bump VERSION →
"1.59.0-ringfix3". Preserve champion consts.

**Purpose:** ISOLATE FIX3 (banana no-carry-in-advance / the backtracking fix) from the E1/E2
economy changes it was bundled with in v1.57.0-ringtune (which reverted −2.4). We never measured
FIX3 alone. This candidate = ringfarm + FIX3 ONLY — nothing else.

## What FIX3 is (user's game-watch finding)
The champion PICKs a banana from the tent, then CARRIES it (walking, sometimes BACKTRACKING to
the tent, passing ripe banana trees) to a plant cell. FIX3 = never pick from the tent in advance:
- **FIX3(i) plant_immediate**: the build-ring PICK fires ONLY when the chosen empty ring cell is
  within RING_PICK_STEPS(=2) of the troll (pick this turn, plant within 1-2 steps — no carrying
  far). If the nearest empty ring cell is >2 away, do NOT PICK (the troll does other work / parks;
  the cell gets built when banking circulation repositions a troll near it).
- **FIX3(ii) harvest_beats_pick**: a ripe BANANA (fruits>0) at/adjacent to the troll (manhattan≤1),
  with harvest_power>0 and free_capacity>0, SUPPRESSES the tent PICK — so the standing harvest(75)
  /seed-move(52) wins and we pick the banana up ON THE WAY instead of a tent errand.

## ★ CRITICAL — strip the E1 contamination
The v1.57 FIX3 commit (`3aebdb2` in branch `worktree-agent-a6215b039a070dcba`) is your
IMPLEMENTATION REFERENCE, BUT it was built on top of FIX1/E1 (`f278d94`) and FIX2/E2 (`b93c41e`),
so its `suppress_ring_pick` line reads:
    `let suppress_ring_pick = ring_active && (plan.want_chopper || harvest_beats_pick);`
The `plan.want_chopper ||` term IS E1 (fund-chopper-first — the prime suspect for the −2.4). YOU
MUST DROP IT. The isolated FIX3 is:
    `let suppress_ring_pick = ring_active && harvest_beats_pick;`   // NO want_chopper
Also DO NOT include FIX2 (diagonal-first plant_cell ordering) — keep ringfarm's existing
nearest-first `plant_cell` (`min_by_key((d[c], tie))`, NOT role_rank). Only FIX3's two gates go in.

NOTE (a bonus of isolating from FIX2): the reviewer's "idle window" concern for v1.57 was a
FIX2×FIX3(i) interaction (diagonal-first picks a FAR diagonal, FIX3(i) blocks it, nearer
orthogonal ignored). WITHOUT FIX2, plant_cell is already the NEAREST empty ring cell, so
plant_immediate is true whenever ANY empty ring cell is within 2 — the idle window largely
dissolves. You should NOT need the "either-role fallback" fix. Verify this reasoning holds in your
implementation; if a stall appears, add the nearest-immediate fallback.

## Where it goes — planner.rs candidates()
The ring build-pick logic (bands 78 build-ring-pick / 77 park-to-pick, gated on ring_active +
plant_cell). Add the two FIX3 gates. Reference 3aebdb2's planner.rs hunk for the exact structure
(RING_PICK_STEPS const, harvest_beats_pick computation, plant_immediate computation, and how they
gate the PICK), but transcribe WITHOUT the want_chopper term and WITHOUT FIX2's plant_cell change.

## Tests (TDD, RED first)
Reuse the two FIX3-specific tests from `3aebdb2`'s `rust/tests/ringtune.rs` (call the file
`rust/tests/ringfix3.rs`): 
1. `ringfix3_no_pick_when_plant_not_immediate`: troll far (>2) from any empty ring cell + tent
   banana → does NOT PICK. RED pre-fix (ringfarm picks whenever ring has a gap).
2. `ringfix3_harvest_ripe_over_tent_pick`: ripe banana adjacent + tent stock → HARVEST, not PICK.
   RED pre-fix.
3. `ringfix3_no_want_chopper_dependency` (NEW — proves the E1 strip): a state with want_chopper
   TRUE + an IMMEDIATE empty ring cell + tent banana + NO adjacent ripe banana → the PICK STILL
   FIRES (because isolated FIX3 does NOT suppress on want_chopper; only E1 did). This is the guard
   that you correctly stripped the E1 term. RED if you left want_chopper in (pick suppressed).
4. Full suite green (baseline 92 tests... actually ringfarm base is at ~ the v1.56 test count —
   check `cargo test --release` count on your base first; ringtune/trainfruit tests are NOT on
   this base). Self-determinism equality 8 seeds.

## ★ THE gate — confirm it's movement-only (not a hidden economy change)
FIX3 changes WHEN bananas are picked (pick-timing/travel), which is mostly execution but touches
ring-build rate. The gate must characterize whether the ECONOMY (banana-wood density) is
materially changed:
- Play >=6 vs boss + >=6 vs Crouistiti (6479836) with a DEBUG probe. REPORT vs the v1.56 ringfarm
  baseline (re-measure ringfarm on the SAME batch for a paired comparison): (a) wood avg (must NOT
  drop — the whole thesis is wood density is load-bearing); (b) ring_planted-by-turn-20 (FIX3(i)
  must not STALL ring-building vs ringfarm's 3-5); (c) backtracking / PICK-then-carry chains
  reduced?; (d) win-rate. If wood drops or the ring stalls, FIX3(i) is hurting the economy — flag
  it (we may keep only FIX3(ii)).
- If the play-API 422s/overloads, get what you can and report partial.

## Resilience + freeze
- COMMIT AFTER EACH PART (FIX3(i), FIX3(ii), tests, gate) — the API has dropped many subagents
  today. If inference errors, commit + stop; you'll be resumed from your last commit.
- Standard freeze: cgauto/submissions/v1.59.0-ringfix3.{rs,min.rs} + data/candidates/ + debug
  probe. bundle/rustc/minify<100KB. Trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

Report: status, commits, test summary (RED each), the exact suppress_ring_pick + plant_immediate
lines you wrote (proving no want_chopper), the paired wood/ring-build/win-rate vs ringfarm,
self-equality, artifact sizes, concerns.
