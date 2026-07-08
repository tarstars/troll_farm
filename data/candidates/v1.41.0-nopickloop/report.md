# Candidate v1.41.0-nopickloop — Builder Report

**Task:** fix a user-observed LIVELOCK: on maps where water + the map edge leave no
reachable plant cell, the starter infinitely PICKs a banana from the tent and banks it
right back (band 88 plant has no cell to offer; band 80 full->bank is suppressed for
banana-carrying starters expecting to plant; the fallback band 10 banks it; PICK (band 50)
fires again next turn) — wasting the whole game for that troll AND blocking scarce
shack-adjacent cells the chopper needs for banking. A companion motion fix (idle-parking
must not clog a scarce camp) rides along, plus a third test (added mid-task by the
controller after design review) pinning that the fix must not over-suppress PICK when a
real plant cell exists on the far side of a tree.

**Worktree state (pre-task, resolved):** `git log --oneline -1` showed `fa33b21` ("feat:
sim Bronze support + tuned wood economy (v0.6.1)") — stale; `git merge-base --is-ancestor
efc3787 HEAD` failed (not an ancestor). Fast-forwarded via `git merge --ff-only
session-2026-07-01` (working tree was clean; no rebase, no history rewrite). Landed on
`73d3c10` ("policy(v2): delta-only verdicts, 5h baseline chaining, noise-calibrated ±0.5
bands"), a strict descendant of the required base `efc3787` and of the most recent
gatekeeper-verdict commit `c2ffec7`/candidate `v1.40.0-roam4` — no intervening drift beyond
already-landed work. Bot crate confirmed at `rust/` per
`docs/superpowers/plans/pipeline-briefs.md`'s "Common context".

## Step 0 — evidence (timeboxed)

Scanned all 290 `data/boss5_games/*/*.raw` DEBUG captures (parsing `@TFMAP` grids, `@TFI P`
initial-plant lines, and `@TFD`/`@TFMOVE` per-turn streams) for the two map-geometry
preconditions the bug needs, plus the position-pinned livelock signature itself:

- **Scarce shack found (stronger than the <=2 asked for):** `shack0` in
  `data/boss5_games/6480914/game_895391723.raw` sits at `(5,4)` with water (`~`) on two
  sides and rock (`#`) on the third — code-verified (not eyeballed) to have exactly **ONE**
  walkable ortho-neighbor, `(6,4)`. This is exactly Test B's precondition (`camp_cells<=2`),
  found on a real captured Boss-5 map.
- **Dead-end BANANA near water found:** `data/boss5_games/6480842/game_895283371.raw` has
  an initial `BANANA` at `(5,2)` (size 4, health 6, 2 fruits) with water at `(5,3)` and rock
  at `(6,2)`/`(5,1)` — code-verified exactly **ONE** walkable ortho-neighbor, `(4,2)`. This
  is exactly Test A's precondition (a plant/dead-end pocket adjacent to water).
- **Direct oscillation signature: not found in this sample.** Our own stdout never logs
  PICK/DROP (per the task brief), so I scanned the one indirect proxy available —
  `my_inventory[BANANA]` (tent stock, logged every turn in `@TFD`) oscillating by exactly +/-1
  every turn for 20+ consecutive turns (the PICK-then-DROP signature). Zero games matched at
  that threshold. A broader "pinned starter" scan (any unit stationary 50+ consecutive
  turns while still issuing MOVE) found 27 hits, but spot-checking the strongest one
  (`6480914/game_895368339.raw`, id 0 pinned exactly 1 cell from its own shack for 254+
  turns) showed `tent_banana` flat at 0 the whole window — a *different* stall (three units
  fully parked, zero production), not this bug. Plausible explanation: these 290 captures
  were gathered for other investigations (motion/phase/race-check), and the specific
  water+edge dead-end geometry is real (see above) but not guaranteed to appear *with* a
  starter that also happens to hold tent bananas in this particular sample.
- **Strong corroborating evidence found instead, directly in the codebase's own history:**
  `rust/src/strategies/mybot.rs:319-343` (an older, pre-R6b-planner strategy) carries the
  comment *"Spot computed for BOTH arms: PICKing without a plantable spot caused a
  PICK<->DROP livelock (cc1 starter, 130 turns in a real arena game)"* and fixes it with the
  identical structural pattern used below: compute the plantable spot once, gate both the
  PLANT and PICK actions on `spot.is_some()`. This is the same bug, previously hit and fixed
  in a real arena game, in an earlier generation of this bot. The R6b joint-planner rewrite
  (`botmain/planner.rs`) reintroduced it because band 50 (PICK) was never wired to band 88's
  plant-cell search. This is treated as the strongest single piece of evidence that the bug
  is real and recurring, and that the fix shape is correct.

## What changed

### `rust/src/botmain/planner.rs`

Hoisted the plant-cell search (previously computed inline, only inside band 88's
`u.carry[BANANA] > 0` guard) into a single `let plant_cell: Option<Cell> = ...` at the top
of the STARTER branch, gated only on `plan.base_trees < plan.farm_cap` (room in the farm),
independent of whether a banana is currently carried. Band 88 now just consumes it:

```rust
if u.carry[BANANA] > 0 {
    if let Some(tc) = plant_cell { ... }   // unchanged rendering
}
```

Band 50/49 (PICK / park-to-pick) now requires `plant_cell.is_some()` in addition to the
existing `inv[BANANA] > 0 && u.free_capacity() > 0`:

```rust
if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
    if manhattan(u.pos(), shack) == 1 { ... Pick ... } else { ... Park (49) ... }
}
```

No other band touched. `fell_ok`/`own_half`/`within_roam`/`race`/`STICKY`/`DENY_W`/
`RACE_SHARE_PEN` are all untouched.

### `rust/src/botmain/motion.rs`

`park_cmd` now checks how many of the shack's ortho-neighbors are walkable
(`camp_cells`); when `<=2`, it first looks for the nearest unclaimed, reachable
manhattan-2-from-shack cell (one ring further out) and parks there instead of on the
scarce cell, falling back to the original `pick_camp_cell` behavior only if no such cell
exists:

```rust
let camp_cells = ortho_neighbors(shack).iter().filter(|c| state.walkable.contains(*c)).count();
if camp_cells <= 2 {
    let ring2 = state.walkable.iter()
        .filter(|c| manhattan(**c, shack) == 2 && !claimed.contains(*c))
        .filter_map(|c| d.get(c).map(|&dist| (*c, dist)))
        .min_by_key(|(c, dist)| (*dist, *c));
    if let Some((c, _)) = ring2 { claimed.insert(c); return format!("MOVE {} {} {}", u.id, c.0, c.1); }
}
let c = pick_camp_cell(state, shack, d, claimed);
format!("MOVE {} {} {}", u.id, c.0, c.1)
```

`bank_cmd` is untouched (a banker genuinely needs the real camp cell now; only *idle*
parking should step back). The `claimed` set is shared with `bank_cmd` calls in the same
render pass, but manhattan-2 ring cells and manhattan-1 camp cells never overlap, so there
is no cross-claiming conflict. The `min_by_key(|(c, dist)| (*dist, *c))` tie-break is a
total order over `(distance, cell)` — required because `state.walkable` is a `HashSet`
whose iteration order is not guaranteed stable across instances in this codebase (per
`state.rs`'s own comment on `tie_salt`/`tie_mix`), matching the determinism convention used
everywhere else in `planner.rs`/`motion.rs`.

### `rust/src/botmain.rs`

```rust
const VERSION: &str = "1.41.0-nopickloop"; // fix: no PICK without a reachable plant cell + scarce-camp parking (user-observed corridor livelock)
```

## TDD

New file `rust/tests/pickloop.rs`, three tests (Test C added mid-task per controller
review of the fix design).

### Test A — `no_pick_without_reachable_plant_cell`

Corridor: shack `(0,2)`; `walkable = {(1,2),(2,2)}`; **both** cells occupied by a fruitless
banana tree (`base_trees=2 < farm_cap=12` says "room" — a tree *count*, not a free-*cell*
check, which is the bug's heart). Starter (`chop_power=0`, so no competing chop-help/
anti-starvation band) stands at `(1,2)` (shack-adjacent), tent holds 3 bananas. Both corridor
cells fail the plant-cell filter (tree-occupied), so `plant_cell = None`.

- **Pre-fix (verified — see RED/GREEN below):** only bands present are Pick (50xBAND,
  since neither the old code nor anything else gated it) and the band-10 Park fallback
  (10xBAND) — Pick wins. Assertion `!cmds[&0].starts_with("PICK")` **fails**.
- **Post-fix:** band 50 is now gated off (`plant_cell.is_some()` is false); only band 10
  (Park) survives, rendered via the now-also-fixed `park_cmd` (camp_cells=1 here too, so it
  steps to `(2,2)` instead of re-occupying `(1,2)`) -> `"MOVE 0 2 2"`. Assertion holds.

### Test B — `scarce_camp_park_leaves_drop_cell_free`

Shack `(0,2)`; `walkable = {(1,2),(1,1),(2,2)}` — `ortho_neighbors((0,2)) n walkable = {(1,2)}`
only, so `camp_cells=1`. A starter already parked at `(2,2)` (a fine, out-of-the-way spot)
calls `motion::park_cmd` directly.

- **Pre-fix (verified):** `pick_camp_cell` has exactly one candidate, `(1,2)` -> `"MOVE 0 1
  2"`. Assertion `assert_ne!(cmd, "MOVE 0 1 2")` **fails**.
- **Post-fix:** the manhattan-2 ring search finds two candidates, `(1,1)` (d=2 from the
  troll) and `(2,2)` (d=0, the troll's own cell) — picks `(2,2)`, i.e. stays put ->
  `"MOVE 0 2 2"`. Assertion holds.

### Test C — `pick_stays_enabled_when_plant_cell_lies_beyond_a_tree` (added mid-task)

False-suppression guard: the gate must not treat a tree-occupied cell as a BFS obstacle
(trees never participate in `bfs_distances`; only `state.walkable`/terrain does — see
`state.rs`). Geometry chosen after checking the exact code semantics (the controller's own
draft geometry, worked out live in the task text, could not fit a genuine "target beyond a
mid-path tree" inside the *default* `farm_r=2`, since that leaves only two in-radius cells
on a linear corridor and there's no room for tree-free-start -> tree -> free-target within
2 hops):

Linear corridor `shack(0,2) -> (1,2) -> (2,2) -> (3,2)`, `farm_r` widened to **3** (a
generic Plan-field choice for this gate test, not tied to the live `GE_FARM_R` constant,
which this test isn't sweeping). Hand-verified distances:

- `farm_d` (BFS from shack): `(1,2)=1, (2,2)=2, (3,2)=3` — all in radius.
- `d` (BFS from the starter at `(1,2)`): `(1,2)=0, (2,2)=1, (3,2)=2` — all reachable.

Trees occupy **both** `(1,2)` (the starter's own cell) and `(2,2)` (the mid-corridor cell),
leaving `(3,2)` as the **unique** surviving plant-cell candidate — reachable only by a BFS
path that runs straight through the tree-occupied `(2,2)`. If a future refactor ever made
the reachability search tree-aware (treating tree cells as obstacles), `d` would strand at
or before `(1,2)`, `(3,2)` would look unreachable, and PICK would be wrongly suppressed.
Fruits are 0 on both trees so bands 52/75 stay silent; `chop_power=0` keeps the chop-help/
anti-starvation bands silent regardless of tree size.

- Confirmed **both** pre-fix and post-fix: `cmds[&0] == "PICK 0 BANANA"` (a non-regression
  pin, not a RED/GREEN test).

### RED/GREEN verification (actually run, not just hand-derived)

1. Wrote `pickloop.rs` against the ALREADY-fixed `planner.rs`/`motion.rs` first (all 3
   green) to confirm the intended-behavior story compiles and is internally consistent.
2. `git stash push -- rust/src/botmain/planner.rs rust/src/botmain/motion.rs` (temporarily
   reverting *only* the two production files, leaving the new test file and the `botmain.rs`
   version bump in place) and reran `cargo test --release --test pickloop`:

```
test pick_stays_enabled_when_plant_cell_lies_beyond_a_tree ... ok
test scarce_camp_park_leaves_drop_cell_free ... FAILED
test no_pick_without_reachable_plant_cell ... FAILED

---- scarce_camp_park_leaves_drop_cell_free stdout ----
assertion `left != right` failed: idle park must not clog the sole scarce camp cell: got MOVE 0 1 2
---- no_pick_without_reachable_plant_cell stdout ----
must not PICK a banana with nowhere reachable to plant it: got PICK 0 BANANA

test result: FAILED. 1 passed; 2 failed; 0 ignored
```

   Exactly the predicted pre-fix failures (A: `PICK 0 BANANA`; B: `MOVE 0 1 2`), and Test C
   passes unconditionally as designed — confirms all three tests are true RED/pinned checks,
   not vacuously-true assertions.
3. `git stash pop` (restored the fix) and reran the full suite — all green (below).

## Gate results

1. **Baseline** (worktree post fast-forward, pre-edit): confirmed clean build.
2. **RED — `pickloop.rs` A & B vs pre-fix code**: exact failure messages above; **C passes
   pre-fix** (as designed).
3. **GREEN — `cargo build --release`** (post-fix): clean, the same 5 pre-existing warnings
   as the `v1.40.0-roam4` baseline (`PLUM` unused import in `printer_bot.rs`, `opp` unused
   variable in `boss_v3.rs`, `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`,
   `Strategy` unused import in `fastcheck.rs`). **No new warnings.**
4. **GREEN — `cargo test --release`** (post-fix): **29 suites** (28 prior + the new
   `pickloop.rs`), **56 passed** (53 + `pickloop.rs`'s 3) **+ 5 ignored + 0 failed**. Every
   other suite's count unchanged from the `v1.40.0-roam4` baseline: `deny_probe` 0+1
   ignored, `motion_corridor` 2, `nanaflow` 2, `phase_factory` 1, `phase_hoard` 7,
   `phase_skeleton` 2, `planner_solver` 3, `planner_tasks` 3, `race_check` 3, `roam` 1,
   `sim_engine_tests` 26, `tactics_scale` 3+4 ignored.
5. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8
   300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams
   identical`.
6. **`tools/bundle.py`** (run from `rust/`): `src/botmain.rs -> target/refactor/bundled.rs:
   77136 chars` (self-reported; actual file is 78,521 B — the ~1.4 KB self-report/file-size
   gap is a pre-existing quirk of `bundle.py`, also present in the `v1.40.0-roam4` report at
   the same relative magnitude, not a new issue). Grep confirms `VERSION: &str =
   "1.41.0-nopickloop"` (single occurrence, expected line).
7. **`rustc --edition 2021 -O`** on the bundled source (dot-free copy): exit 0
   (SRC-COMPILE-OK).
8. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8
   seeds x 2 seats), all command streams identical`.
9. **`tools/minify.py`**: `77136 -> 44286 chars (57%)` (actual file: 44,286 B) — 56% under
   the 100,000 B cap.
10. **`rustc --edition 2021 -O`** on the minified copy (dot-free copy): exit 0
    (MIN-COMPILE-OK).
11. **Minified bin vs `target/release/bot`**: `EQUAL: 16 games (8 seeds x 2 seats), all
    command streams identical`.
12. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Bundled debug
    source: 78,520 B (1 byte shorter than the release bundled `.rs`, as expected).
    `rustc --edition 2021 -O` compile-check: exit 0. Minified: `77135 -> 44285 chars (57%)`
    (1 byte shorter than the release `.min.rs`, matching the pattern seen on every prior
    candidate's probe). `rustc --edition 2021 -O` compile-check: exit 0 (DBG-COMPILE-OK).
    2-seed local smoke: `./target/release/equality <probe> target/release/bot 2 300
    target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical` (no crash; DEBUG only echoes to stderr, so stdout-parity holds).
13. **Champion-equality: N/A by design**, per the task's own framing ("NO champion equality
    (behavior change)") — this candidate intentionally changes behavior (suppresses PICK/
    park-to-pick on maps with no reachable plant cell; changes idle-park behavior near a
    scarce camp). Self-determinism (gate 5) and the bundle/minify round-trip equalities
    (gates 8, 11) already establish full determinism and shuffle-invariance on the existing
    corpus of behavior (every prior test scenario uses open, farm-rich rooms where
    `plant_cell` is always found and `camp_cells` is always >2, so none of them exercise the
    new gates) — that is a different, weaker guarantee than champion-equality and is not
    conflated with it here.

## Sizes

- `cgauto/submissions/v1.41.0-nopickloop.rs`: **78,521 B** (bundled, comments retained).
- `cgauto/submissions/v1.41.0-nopickloop.min.rs`: **44,286 B** (56% under the 100,000 B cap).
- `data/candidates/v1.41.0-nopickloop/v1.41.0-nopickloop.rs` / `.min.rs`: byte-identical
  (`cmp`-verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.41.0-nopickloop/v1.41.0-nopickloop.debug-probe.min.rs`: **44,285 B**
  (DEBUG=true; 1 byte shorter than the release `.min.rs`).

## Diffstat

```
rust/src/botmain.rs          |  2 +-
rust/src/botmain/motion.rs   | 20 +++++++++++++++++++-
rust/src/botmain/planner.rs  | 35 +++++++++++++++++++++++++++++------
rust/tests/pickloop.rs       | 221 ++++++++++++++++++++++++++++++++++++++++++++++++  (new file)
4 files changed, 49 insertions(+), 8 deletions(-) in tracked files + pickloop.rs new
```

## Scope discipline

Only the plant-cell hoist + `plant_cell.is_some()` gate (planner.rs), the scarce-camp
branch in `park_cmd` (motion.rs), and `VERSION` (botmain.rs) were touched. NOT touched:
`fell_ok`/`own_half`/`within_roam`/`race`/`STICKY`/`DENY_W`/`RACE_SHARE_PEN` (planner.rs's
felling machinery), `bank_cmd`/`pick_camp_cell`/`watchdog`/`solve_moves` (motion.rs's other
functions), `tactics.rs` (training ladder, phase, farm geometry constants), or any of the
`GE_*` constants besides the version string. `rust/src/strategies/mybot.rs` (the older
pre-R6b strategy that independently fixed this same bug historically) was read for evidence
but is dead code outside the live bot crate per `pipeline-briefs.md`'s "Common context" —
not touched.

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` then vs field (incl. >=1 denial-style
opponent — mikdiet 6480914 / plcc 6480966 — and >=1 >=19.6 player per `field_targets.py`).
Read `cgauto/ramp.py --last 8` (wood >=45, t300 delta vs -15.3 baseline) and telemetry from
the newest `.raw` files (`@TFFARM` / `@TFPHASE`). Expected signature: this is a pure bug fix
with no farm-geometry/economy-constant changes, so on the majority of maps (open, farm-rich)
behavior should be **byte-identical** to `v1.40.0-roam4` (plant_cell is always found,
camp_cells is always >2) — watch specifically for (a) any regression on maps where a
starter previously happened to PICK productively near map edges/water (i.e. confirm the
gate isn't over-firing outside the two constructed unit-test scenarios — Test C is the
guard for this, but real maps have geometry the unit tests can't fully anticipate); (b)
whether real Boss-5/field games actually contain the livelock (Step 0 found the map
*geometry* preconditions are real and common — 98 scarce-shack hits, 62 dead-end-banana
hits across 290 games — but couldn't directly observe the PICK-loop symptom itself in this
sample, so the arena/gatekeeper read is the first real confirmation this fix moves anything
measurable); (c) whether the scarce-camp parking change measurably reduces self-block/
chopper-denied-bank turns on tight maps (a plausible secondary contributor to the documented
late-throughput-ceiling, since a blocked bank cell directly throttles chopper throughput).

## Fix: reviewer CRITICAL (park intents) + MINOR (band-80 alignment)

A task reviewer audited this candidate and found one CRITICAL and one MINOR defect in the
fix above. Both are corrected here, TDD-style, in the same worktree/candidate (`VERSION`
stays `1.41.0-nopickloop` — this is a fix to the same candidate, not a new one).

### CRITICAL — `park_cmd`'s ring-2 redirect swallowed the goal-directed park-to-pick errand

`motion::park_cmd`'s scarce-camp ring-2 redirect (added by the fix above) was dispatched
for **every** `Kind::Park` candidate, but the planner pushes `Kind::Park` for two different
intents:

- band 10 (`target: None`) — idle parking, no destination requirement, free to step back
  to a ring-2 cell out of the banker's way.
- band 49 (`target: Some(shack)`) — the park-to-pick ERRAND: a starter walking toward the
  shack so it can PICK (band 50) once it reaches manhattan==1. This is goal-directed.

Redirecting the errand through the ring-2 detour breaks its convergence: `claimed` is a
fresh `HashSet` every `assign()` call, so once the redirected troll reaches its own ring-2
cell, next turn `park_cmd` again sees that very cell as the nearest **unclaimed**
manhattan-2 option (distance 0 from itself) and reissues `MOVE <id> <self.x> <self.y>` —
forever. The anti-stall watchdog can't catch it: it only sidesteps a MOVE whose target
differs from the troll's current cell, and a self-target MOVE never does. On any
scarce-camp map (<=2 walkable shack neighbors) this is a **permanent stall**, not a
slowdown.

**Fix:** `park_cmd` gained an explicit `idle: bool` parameter (one function, one flag — no
duplicated motion logic, per the reviewer's instruction). The ring-2 branch is now guarded
by `if idle`; when `idle=false` it falls straight through to the original
`pick_camp_cell`-only behavior. The dispatch site (`planner.rs`, `assign()`'s render loop)
now distinguishes the two `Kind::Park` intents by their `target` field:

```rust
(Kind::Park, park_target) => {
    motion::park_cmd(state, plan.shack, u, &d, &mut claimed_drop, park_target.is_none())
}
```

`park_target.is_none()` is `true` only for band 10 (idle); band 49's errand
(`target: Some(shack)`) always gets `idle=false` and the direct camp approach.

### MINOR — band 80 (full -> bank) still gated on the tree-COUNT, not the hoisted `plant_cell`

Bands 88/50/49 already gate on `plant_cell.is_some()` (an actual reachable free cell), but
band 80's carrier-exclusion (`!(!is_chopper && u.carry[BANANA] > 0 && ...)`) still used the
older, coarser `plan.base_trees < plan.farm_cap` (a tree *count*, not a free-*cell*
check — the same mismatch the original fix closed for PICK). A full starter carrying a
banana on a farm that has "room" by tree-count but nowhere actually reachable to plant
would be excluded from banking, waiting indefinitely for a spot that never opens.

**Fix:** hoisted the `plant_cell` computation from inside the STARTER (`else`) branch to
before band 95/80 (i.e. above the `is_chopper` split), so it's computed once per troll —
chopper included, harmlessly unused there — and referenced by band 80 too:

```rust
if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plant_cell.is_some())
{
    out.push(Cand { kind: Kind::Bank, target: None, value: 80 * BAND });
}
```

Bands 88/50/49 inside the STARTER branch are unchanged except that they now consume the
hoisted variable instead of redeclaring it. This is semantically better, not just aligned:
a carried banana with no plantable cell should be banked (closing the loop's other half),
not held hostage waiting for room.

### TDD

**New covering test** (`rust/tests/pickloop.rs`): `errand_reaches_pick_on_scarce_map` — the
reviewer's exact scenario. Shack `(0,2)` with a single walkable ortho-neighbor `(1,2)`
(`camp_cells=1 <= 2`, scarce-camp branch live); corridor
`walkable = {(1,2),(2,2),(3,2),(4,2),(5,2)}`; no trees (plant-cell gate open everywhere in
range); tent holds 1 banana; `base_trees=0 < farm_cap=12` with `farm_r=5` so a reachable
plant cell always exists (the gate stays open throughout); pure (`chop_power=0`) starter
begins at the far end `(5,2)`. Drives `assign()` for up to 12 simulated turns, teleporting
the lone starter to each `MOVE` target (single troll, no conflicts) until `PICK` fires.

**RED (verified against pre-fix code, `cargo test --release --test pickloop`):**

```
running 4 tests
test no_pick_without_reachable_plant_cell ... ok
test pick_stays_enabled_when_plant_cell_lies_beyond_a_tree ... ok
test errand_reaches_pick_on_scarce_map ... FAILED
test scarce_camp_park_leaves_drop_cell_free ... ok

failures:

---- errand_reaches_pick_on_scarce_map stdout ----
thread 'errand_reaches_pick_on_scarce_map' panicked at tests/pickloop.rs:317:5:
the park-to-pick errand must reach PICK within 12 turns; starter stalled at (2, 2)

test result: FAILED. 3 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Stalled exactly where predicted: the ring-2 redirect's only manhattan-2 candidate in this
corridor is `(2,2)`; once there, `park_cmd` re-picks it as its own nearest-unclaimed ring-2
cell every turn (distance 0) and never moves again.

**GREEN (post-fix, `cargo test --release --test pickloop`):**

```
running 4 tests
test no_pick_without_reachable_plant_cell ... ok
test errand_reaches_pick_on_scarce_map ... ok
test scarce_camp_park_leaves_drop_cell_free ... ok
test pick_stays_enabled_when_plant_cell_lies_beyond_a_tree ... ok

test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

The errand now reaches PICK in 2 simulated turns: turn 0 dispatches the direct
`pick_camp_cell` approach (`MOVE 0 1 2`, the only camp cell), turn 1 the starter is
shack-adjacent and band 50 fires `PICK 0 BANANA`.

Existing test B (`scarce_camp_park_leaves_drop_cell_free`) was updated to pass the new
`idle` parameter explicitly (`motion::park_cmd(&state, (0, 2), &starter, &d, &mut claimed,
true)`) — it exercises band-10 idle parking, so `idle=true` preserves its original intent
and assertion unchanged.

### Gate results (re-run after both fixes)

1. **GREEN — `cargo build --release`**: clean, the same 5 pre-existing warnings as before
   (unchanged: `PLUM` unused import in `printer_bot.rs`, `opp` unused variable in
   `boss_v3.rs`, `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`, `Strategy` unused
   import in `fastcheck.rs`). **No new warnings.**
2. **GREEN — `cargo test --release`**: **29 suites** (unchanged), **57 passed** (56 + the
   new `errand_reaches_pick_on_scarce_map`) **+ 5 ignored + 0 failed**. `pickloop.rs` now
   runs 4 tests (was 3), all green. Every other suite's count unchanged.
3. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8
   300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams
   identical`.
4. **`tools/bundle.py`**: `src/botmain.rs -> target/refactor/bundled.rs: 79481 chars`
   (actual file: 80,880 B — the usual multi-byte-UTF8-comment gap, e.g. em dashes, same
   pattern as every prior candidate report). Grep confirms `VERSION: &str =
   "1.41.0-nopickloop"` still the single occurrence (unchanged — this is a fix to the same
   candidate).
5. **`rustc --edition 2021 -O`** on the bundled source (dot-free copy): exit 0
   (SRC-COMPILE-OK).
6. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8
   seeds x 2 seats), all command streams identical`.
7. **`tools/minify.py`**: `79481 -> 44359 chars (55%)` (actual file: 44,359 B) — 56% under
   the 100,000 B cap.
8. **`rustc --edition 2021 -O`** on the minified copy (dot-free copy): exit 0
   (MIN-COMPILE-OK).
9. **Minified bin vs `target/release/bot`**: `EQUAL: 16 games (8 seeds x 2 seats), all
   command streams identical`.
10. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Bundled debug
    source: 80,879 B (1 byte shorter than the release bundled `.rs`, as expected). `rustc
    --edition 2021 -O` compile-check: exit 0. Minified: `79480 -> 44358 chars (55%)` (1 byte
    shorter than the release `.min.rs`, matching the pattern seen on every prior candidate's
    probe). `rustc --edition 2021 -O` compile-check: exit 0 (DBG-COMPILE-OK). 2-seed local
    smoke: `./target/release/equality target/refactor/min_debug_bin target/release/bot 2
    300 target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical`.
11. **Frozen artifacts re-verified byte-identical** to the exact gate-checked scratch copies
    (`cmp` against `target/refactor/{bundled,min,min_debug}_check.rs`) before overwriting —
    no drift between what was gated and what was frozen.

### Sizes (updated)

- `cgauto/submissions/v1.41.0-nopickloop.rs`: **80,880 B** (bundled, comments retained; was
  78,521 B — grew from the new doc comments explaining the `idle` split and the hoisted
  `plant_cell`, not from any logic growth).
- `cgauto/submissions/v1.41.0-nopickloop.min.rs`: **44,359 B** (56% under the 100,000 B cap;
  was 44,286 B).
- `data/candidates/v1.41.0-nopickloop/v1.41.0-nopickloop.rs` / `.min.rs`: byte-identical
  (`cmp`-verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.41.0-nopickloop/v1.41.0-nopickloop.debug-probe.min.rs`: **44,358 B**
  (DEBUG=true; 1 byte shorter than the release `.min.rs`).

### Diffstat (this fix, on top of the original candidate commit)

```
rust/src/botmain/motion.rs  |  49 +++++++++++++-------
rust/src/botmain/planner.rs | 106 ++++++++++++++++++++++++++------------------
rust/tests/pickloop.rs      | 105 ++++++++++++++++++++++++++++++++++++++++++-
3 files changed, 197 insertions(+), 63 deletions(-)
```

(plus the re-frozen `cgauto/submissions/`/`data/candidates/` copies above — mechanical
regenerations of the same source, no independent edits.)

### Scope discipline

Touched only: `motion::park_cmd`'s signature/body (added `idle: bool`, gated the ring-2
branch on it), the one `Kind::Park` dispatch arm in `planner.rs::assign`, the hoist of
`plant_cell` + band 80's guard clause in `planner.rs::candidates`, the one call site in
`tests/pickloop.rs` (test B) needing the new parameter, and the new covering test (test D).
NOT touched: `bank_cmd`/`pick_camp_cell`/`watchdog`/`solve_moves` (motion.rs), any other
band (70/72/31/30/95/88/75/62/60/58/45/44/52/40/42/10), `fell_ok`/`own_half`/`within_roam`/
`race`/`STICKY`/`DENY_W`/`RACE_SHARE_PEN`, `tactics.rs`, or `VERSION` (this is a fix to the
same candidate, not a new one).
