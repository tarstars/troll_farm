# v1.54.0-frontdoor builder brief — front-door farm placement (fix the shack-bridged farm_d)

**Origin:** user replay review of game 895493013 (Sasso_Stark) + a joint re-diagnosis
(2026-07-09). This SUPERSEDES the earlier-wrong D4 tentgap theory (shacks are NOT walkable;
the tent is correctly impassable).

## Verified root cause (do NOT re-derive — confirmed against code + replay)
`farm_d = bfs_distances(&state.walkable, &[state.my_shack])` (tactics.rs:98) is a BFS **seeded
at the shack cell**. The shack is impassable to trolls (they can't re-enter it), but the BFS
uses it as a zero-cost hub, so cells on OPPOSITE sides of the shack both read farm_d≈1. The
plant filter `farm_d <= farm_r (2..3)` then admits farm cells on BOTH sides of the shack.
On maps where the shack sits on a chokepoint (Sasso: lake + boulders), the two sides are ~24
REAL steps apart (whole walkable area is ONE connected component — it's a DISTANCE problem, not
connectivity). Measured impact in 895493013: the gatherer (troll 1) spent **87% of the game
(263/300 turns) in pure transit**, shuttling ~24 steps each way to tend far-side bananas.
Confirmed numbers: farm_d(14,4)=1 but real dist (12,4)->(14,4)=24; four east cells read
farm_d<=2 while being 23-25 real steps from the west farm.

## The model (agreed with the user)
The shack is NOT a hub a troll can stand on — the gatherer works from ONE walkable cell
adjacent to the shack (the "front door"). Farm cells should be a compact cluster within a
small TRUE-walking radius of that door, all on one reachable side.

**Door selection (user's rule): farthest-from-enemy among VIABLE sides.**
- Door candidates = the shack's walkable orthogonal neighbors.
- A candidate door n is VIABLE if it can host a farm: at least `MIN_FARM_CELLS` (propose 4)
  plantable cells within `door_d(n) <= farm_r`, where door_d(n) = BFS from n over walkable.
- Among viable doors, pick the one with the LARGEST true-BFS distance from the OPPONENT shack
  (`opp_d = bfs_distances(walkable, [opp_shack])`, maximize opp_d[door]). Rationale: the enemy
  must travel farther to raid our crops (a free defensive orientation on a choice we must make
  anyway). Deterministic tie-break (e.g. lexicographic cell) if equal.

**Chokepoint gating (CRITICAL — keep it a NO-OP on normal maps):** only change behavior when
the shack actually straddles a chokepoint. Detect: max over pairs of door-candidates of the
true distance between them > `CHOKE_THRESHOLD` (propose 8; on open maps opposite neighbors are
~4 apart via the small detour around the shack, on Sasso they are 24). 
- NOT a chokepoint -> farm eligibility UNCHANGED (`farm_d <= farm_r`, exactly as today).
- IS a chokepoint -> farm eligibility = `door_d(chosen_door) <= farm_r` (compact one-side
  cluster). This is the ONLY behavior change, and only on chokepoint maps.

Keep `farm_d` (BFS from shack) for its OTHER uses (banking-adjacency: `farm_d==1` identifies
shack-adjacent cells — planner.rs:323 bank_adj etc.). Do NOT repurpose farm_d wholesale; ADD a
door-based eligibility that only overrides the plant filter under the chokepoint condition.

## Where the code lives
- `tactics.rs:98` farm_d; `:135`,`:241` farm/plant candidate filters (`farm_d <= farm_r`).
- `planner.rs:307-325` plant_cell selection (`farm_d <= farm_r`), `:323` bank_adj (farm_d==1),
  `:587` printer bands. These are the farm-eligibility sites to route through the new logic.
- `Plan` (tactics.rs) likely needs a new field: either the chosen `door`, a `door_d` map, or a
  precomputed `farm_ok: HashSet<Cell>` (the eligible-farm-cell set). A precomputed eligible-set
  on the Plan is probably cleanest (compute once in plan(), consume in planner). Match the
  existing Plan/field style.

## Tests (TDD, RED first, record actual failing output)
1. `frontdoor_sasso_straddle_fixed`: reduced Sasso-like fixture (shack on a chokepoint, farm
   cells reachable both sides but ~20+ apart). Assert the eligible farm-cell set is entirely on
   ONE side; assert a specific far-side cell that is farm_d<=2 is NOT eligible. RED pre-fix
   (both sides eligible).
2. `frontdoor_open_map_noop`: open map, shack in the clear. Assert the eligible farm-cell set ==
   the old `farm_d <= farm_r` set exactly (no change). Must pass pre- AND post-fix (the no-op
   guard). Flip-check: if you disable the chokepoint gate, this test should FAIL (proving the
   gate is load-bearing) — document it, then restore.
3. `door_farthest_from_enemy`: chokepoint map with TWO viable sides at different distances from
   the opponent shack. Assert the chosen door is the farther one. Flip the opp_shack position
   and assert the door flips.
4. `door_viability_floor`: chokepoint map where the farthest side has < MIN_FARM_CELLS cells.
   Assert we fall back to a viable (nearer) side rather than picking the cramped far side.
5. Determinism: any HashMap/HashSet iteration in the new code uses canonical (sorted) order.

## Gates (standard builder procedure — docs/superpowers/plans/pipeline-briefs.md §builder)
- `cargo test --release` all green (current baseline 76 pass) + your new tests.
- Self-determinism equality 8 seeds EQUAL.
- ★ CHAMPION-EQUALITY on OPEN maps: because the change is a no-op off chokepoints, a stream-
  equality run vs the pre-frontdoor build should be EQUAL on the vast majority of random seeds
  (open maps); it may differ only on the rare chokepoint seed. Run equality vs the frozen
  pre-frontdoor artifact over >=16 seeds and REPORT how many differ (expect ~0; any difference
  should be a genuinely chokepoint map — spot-check one).
- bundle -> rustc --edition 2021 -O -> minify <100KB -> compile-check minified.
- VERSION -> "1.54.0-frontdoor". Base = current session-2026-07-01 HEAD (the accumulated
  champion line; VERSION is currently 1.53.0-pressurefarm — that's the intended base; the
  frontdoor change is orthogonal to the parked-but-inert governor and to splitclaims).
- Freeze artifacts to cgauto/submissions/ + data/candidates/v1.54.0-frontdoor/ + debug probe.
- Commit in the worktree with the trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## Notes for later stages (not the builder's job)
- Gate: this is an execution waste-cut; expect map-dependent gains (large only on chokepoint
  maps, none elsewhere) — do NOT expect a uniform boss-pool wood lift. The real test is the arena.
- Arena isolation: baseline = the PRE-frontdoor tree (the 1.53 artifact), so the delta measures
  frontdoor alone, not the splitclaims/governor drift from yield.
