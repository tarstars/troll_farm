# Candidate v1.37.0-nanaflow — Builder Report

**Task:** BANANA TREE-FIRST harvesting (finding #2) + DIAGONAL plant placement (finding #3),
user replay-review, spec Amendment 2. Builder role only. Base tree: worktree verified at
`30263ca` ("policy(arena): slot-saturation queue…"), which sits directly on top of `4841ffc`
("feat(race): doomed-target race check…", the v1.36.0-race candidate) — `git diff --stat
4841ffc 30263ca -- rust/` is empty, so the pre-existing baseline for this candidate is
exactly v1.36.0-race's gated state (confirmed below). Champion-equality gate explicitly
waived per the brief (behavior changes by design in both mechanisms) — no comparison run
against `cgauto/submissions/v1.28.3-sticky6.min.rs`.

## What changed

Both changes live entirely in `rust/src/botmain/planner.rs`'s `candidates()` (the L2 joint
task-assignment value bands). `rust/src/botmain.rs`: `VERSION` → `"1.37.0-nanaflow"` only —
no other constants touched (no fell/funding/race-band/seed_cells changes, per scope
discipline).

### A) TREE-FIRST banana harvesting (finding #2)

The printer section (`if plan.base_trees < plan.farm_cap { … }`) used to PICK the banked
tent ahead of harvesting a ripe seed tree directly, and the tree-seek was only even
*considered* once the tent was completely empty — backwards, since harvesting a tree
directly converts fruit straight into a farm seed, while tent stock is just as bankable a
turn later.

**Band table — before:**

| Band | Kind | Trigger | Gate |
|---|---|---|---|
| 50·BAND | Pick | `inv[BANANA]>0 && free_capacity>0`, shack-adjacent | none |
| 50·BAND−1 | Park | same, NOT shack-adjacent (walk to the tent) | none |
| 48·BAND−eta | MoveTo (ripe banana / water-adjacent apple tree) | fruits>0, reachable | **`inv[BANANA] == 0`** (tent must be empty first) |

**Band table — after:**

| Band | Kind | Trigger | Gate |
|---|---|---|---|
| 52·BAND−eta | MoveTo (ripe banana / water-adjacent apple tree) | fruits>0, reachable | **none** — gate removed, harvested even with tent stock on hand |
| 50·BAND | Pick | `inv[BANANA]>0 && free_capacity>0`, shack-adjacent | none (unchanged; now the fallback) |
| 50·BAND−1 | Park | same, NOT shack-adjacent | none (unchanged; now the fallback) |

Net effect: a reachable ripe seed tree always outranks the tent (52 > 50); the tent
(PICK/Park, still 50/49) is only reached once no ripe seed tree is reachable. Excess
bananas accumulate in the tent via the pre-existing full->bank flow (1pt banked each, or 8pt
later via plant->fell, 2 wood @ 4pt).

Code (the only touched block, `candidates()` section 5 "PRINTER"):
```rust
if plan.base_trees < plan.farm_cap {
    for p in state.trees.iter().filter(|p| {
        p.fruits > 0
            && d.contains_key(&p.pos())
            && (p.tree_type == "BANANA"
                || (p.tree_type == "APPLE"
                    && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1)))
    }) {
        let pc = p.pos();
        out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 52 * BAND - eta(&d, pc, ms) });
    }
    if inv[BANANA] > 0 && u.free_capacity() > 0 {
        if manhattan(u.pos(), shack) == 1 {
            out.push(Cand { kind: Kind::Pick, target: Some(shack), value: 50 * BAND });
        } else {
            out.push(Cand { kind: Kind::Park, target: Some(shack), value: 50 * BAND - 1 });
        }
    }
}
```
(The standing-on-a-ripe-fruit Harvest band, 75, and the Hoard-only wallet band, 62, are
untouched — they already outrank/underrank 52 respectively and were not part of this fix.)

### B) DIAGONAL plant placement (finding #3)

The plant-cell chooser (STARTER band 88, `u.carry[BANANA] > 0` branch) picked the free farm
cell with `min_by_key((d[c] + wet-bonus, tie_mix))` — pure map-distance, blind to the cell's
relationship to the shack. That let it happily plant on the four cells **orthogonally**
adjacent to the shack — exactly the four bank/DROP cells every hand's carry trip needs —
congesting the farm's only bank-access points.

**Key formula — before:** `(d[c] + if wet {0} else {2}, tie_mix(c, salt))`

**Key formula — after:** `(d[c] + if wet {0} else {2} + geo, tie_mix(c, salt))`, where
`geo = (if bank_adj {3} else {0}) + (if diag {-1} else {0})`, `bank_adj = farm_d[c] == 1`
(orthogonal-to-shack, the 4 bank/DROP cells), `diag = |dx|==1 && |dy|==1` relative to
`plan.shack`.

Net effect: at equal map-distance the four orthogonal bank cells are now penalized (+3,
map-distance-equivalent) and the four diagonal cells are rewarded (-1) — diagonal cells win
any tie against an orthogonal cell one step further out, and always win against an
orthogonal cell at the SAME distance class the old code preferred by raw proximity. `wet`
and `tie_mix` tie-break are untouched.

Code (the only touched block, `candidates()` section "STARTER -- 1) plant carried banana"):
```rust
.min_by_key(|c| {
    let wet = state.water_cells.iter().any(|w| manhattan(*w, **c) == 1);
    let bank_adj = plan.farm_d.get(*c).copied() == Some(1);
    let (cx, cy) = **c;
    let diag = (cx - plan.shack.0).abs() == 1 && (cy - plan.shack.1).abs() == 1;
    let geo = (if bank_adj { 3 } else { 0 }) + (if diag { -1 } else { 0 });
    (d[*c] + if wet { 0 } else { 2 } + geo, tie_mix(**c, salt))
})
```

### New test file: `rust/tests/nanaflow.rs`

Helpers copied verbatim from `tests/planner_tasks.rs` (`base_state`/`base_plan`/`starter`/
`banana`; `chopper()` omitted, unused by either test). Two tests:

- `ripe_seed_tree_outranks_banked_tent_stock`: tent holds `my_inventory[BANANA]=5`; a ripe
  banana tree (`banana(4,2,4)` with `.fruits=3`) sits within the farm; starter at `(1,2)` is
  shack-adjacent (so PICK, not Park, is the pre-fix winner). Asserts `cmds[&0].contains("4
  2")`.
- `plant_prefers_diagonal_cell_over_orthogonal_bank_cell`: `state.walkable` restricted to
  exactly `{(1,2), (1,1)}` (isolates the geometry terms from any other tie -- the full 8x5
  grid has a SECOND diagonal cell, `(1,3)`, at the same map-distance as `(1,1)`, which would
  make the fixed key ambiguous without narrowing the candidate set). The starter stands on
  the shack cell itself so its own BFS travel distance to each candidate equals `farm_d`
  exactly (map-distance 1 vs 2), matching the brief's "map-distance 1 beats 2" framing.
  Asserts the command contains `"1 1"` and does not contain `"MOVE 0 1 2"`.

**TDD, both confirmed FAILING pre-fix** (`cargo test --release --test nanaflow` run against
the unmodified `planner.rs`):
```
test plant_prefers_diagonal_cell_over_orthogonal_bank_cell ... FAILED
  panicked: should prefer the diagonal cell, off the bank-traffic path: MOVE 0 1 2
test ripe_seed_tree_outranks_banked_tent_stock ... FAILED
  panicked: starter should head for the ripe seed tree ahead of the tent: PICK 0 BANANA
```
Both failures match the brief's predicted pre-fix outputs exactly (`PICK 0 BANANA`; picks
the orthogonal cell `(1,2)`). After implementing A) and B) above, both pass (see gate 4
below) with no changes to the tests themselves.

## Gate results

1. **Baseline** (pre-existing, inherited from v1.36.0-race -- confirmed no `rust/` diff
   between `4841ffc` and this worktree's start commit `30263ca`): 25 suites, 49 passed + 4
   ignored + 0 failed.
2. **RED**: `cargo test --release --test nanaflow` on the unmodified tree -> 2 FAILED, exact
   messages quoted above.
3. **cargo build --release** (post-change): clean, exactly the same 4 pre-existing lib
   warnings (`PLUM` unused import in `printer_bot.rs`, `opp` unused var in `boss_v3.rs`,
   `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`) + 1 pre-existing bin warning
   (`Strategy` unused import in `fastcheck.rs`) -- verified via `touch src/botmain.rs && cargo
   build --release 2>&1 | grep -E "^warning|-->"` (forces a full rebuild so nothing is
   masked by incremental caching) -- **no new warnings**.
4. **GREEN -- cargo test --release** (post-change): **26 suites**, all green. New
   `nanaflow.rs`: 2 passed. Every pre-existing suite unchanged: `motion_corridor` 2,
   `phase_factory` 1, `phase_hoard` 7, `phase_skeleton` 2, `planner_solver` 3,
   `planner_tasks` 3, `race_check` 2, `sim_engine_tests` 26, `tactics_scale` 3 passed + 4
   ignored (the T-hand-parked ignores, untouched by this candidate). **Total: 51 passed + 4
   ignored + 0 failed across 26 suites** (15 empty unittest bins + 10 integration test files
   + 1 doctest).
5. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8
   300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams
   identical`.
6. **tools/bundle.py**: `src/botmain.rs -> target/refactor/bundled.rs: 72770 chars`. Grep
   confirms `VERSION: &str = "1.37.0-nanaflow"`, the untouched `const RACE_SHARE_PEN: i64 =
   2;` (scope check -- the race mechanism from v1.36.0-race is present and unmodified), the
   new `52 * BAND` printer push, and the `bank_adj`/`diag` lines in the plant-cell chooser.
7. **rustc --edition 2021 -O** on the bundled source (dot-free copy): exit 0, zero warnings
   (`SRC-COMPILE-OK`).
8. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8
   seeds x 2 seats), all command streams identical`.
9. **tools/minify.py**: `72770 -> 43533 chars (59%)` -- 56% under the 100,000 B cap.
10. **rustc --edition 2021 -O** on the minified copy (dot-free copy): exit 0
    (`MIN-COMPILE-OK`).
11. **Minified bin vs target/release/bot**: `EQUAL: 16 games (8 seeds x 2 seats), all
    command streams identical`.
12. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Minified: `72769 ->
    43532 chars (59%)`. `rustc --edition 2021 -O` compile-check: exit 0 (`DBG-COMPILE-OK`).
    2-seed local smoke: `./target/release/equality <probe> target/release/bot 2 300
    target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical` (DEBUG only echoes to stderr, so stdout-parity holds).
13. **Champion-equality: N/A by design** (per brief) -- not run. Both mechanisms
    intentionally change behavior (tree-first re-ranks a live band; diagonal placement adds
    two new key terms), so a flag-off/champion-identity gate does not apply here the way it
    did for a purely-additive, narrowly-scoped fix. Self-determinism (gate 5) and the
    bundle/minify round-trip equalities (gates 8, 11) confirm the change is fully
    deterministic and shuffle-invariant in self-play, and are not conflated with
    champion-equality.

## Sizes

- `cgauto/submissions/v1.37.0-nanaflow.rs`: **74,136 B** (bundled, comments retained; byte
  count exceeds the reported char count because the codebase's comments use multi-byte
  UTF-8 typography -- em dashes, arrows -- that minification later strips).
- `cgauto/submissions/v1.37.0-nanaflow.min.rs`: **43,533 B** (56% under the 100,000 B cap).
- `data/candidates/v1.37.0-nanaflow/v1.37.0-nanaflow.rs` / `.min.rs`: byte-identical
  (`cmp`-verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.37.0-nanaflow/v1.37.0-nanaflow.debug-probe.min.rs`: **43,532 B**
  (DEBUG=true; 1 byte shorter than the release `.min.rs` because `false`->`true` is one
  character shorter).

## Diffstat

```
rust/src/botmain.rs         |  2 +-   (VERSION only)
rust/src/botmain/planner.rs | 41 ++++++++++++++++++++++++++--------------  (tree-first + diagonal placement)
rust/tests/nanaflow.rs      | new file, 141 lines, 2 tests
```

## Scope discipline

Only the two named mechanisms were touched. NOT touched: fell bands (70/72/40/42/30/31,
including the v1.36.0-race `race()` helper -- confirmed present verbatim in the bundle grep
above), funding bands (60/58/65/64/63/45/44), the Hoard wallet band (62), `seed_cells`/
`fell_ok`'s protection logic, `GE_MAX_TROLLS`/training/tactics.rs, or motion.rs. The
"keep grown diagonal fruiters" protection idea from finding #3 is explicitly deferred per
the spec amendment (a separate, strictly-gated sub-candidate) -- nothing here reserves or
protects a farm cell from felling.

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` + field (incl. >=1 denial-style opponent
-- mikdiet 6480914 / plcc 6480966 -- and >=1 >=19.6 player per `field_targets.py`). Expected
signature: this is a pure execution/efficiency fix (harvest ordering + plant geometry), not
an economy-band change, so `ramp.py --last 8` wood/delta numbers should stay in-band or
improve slightly (less bank-cell congestion, less tent-then-tree double-travel); no crater
expected. Watch specifically for: (a) `@TFFARM`/`@TFPHASE` telemetry showing farm fill rate
(base_trees approaching farm_cap) improving or holding steady -- the diagonal change trades a
small distance cost for reduced self-blocking at the four DROP cells, so on tight/narrow
maps where the bank cells are already a bottleneck this should show up as fewer stalls; (b)
no regression on maps with very few reachable ripe trees (tree-first should never make
things worse there, since band 52 only ever fires when a reachable ripe tree exists -- the
tent fallback is otherwise identical to today's champion behavior).

## Mini-gate (v1.37.0-nanaflow, boss 6)

**Role: GATEKEEPER, REDUCED probe** (crater-insurance before an arena submit; economy-band
changes are the historically crater-prone class). Scope: boss games ONLY, no field games, per
the reduced-probe instruction (arena mid-goal-verification on v1.36.0-race, budget-fresh but
speed matters).

**Probe verification** (`data/candidates/v1.37.0-nanaflow/v1.37.0-nanaflow.debug-probe.min.rs`,
43,532 B): `DEBUG: bool = true` (1 hit, confirmed) / `1.37.0-nanaflow` present / `52 * BAND`
present (the tree-first printer push, confirmed byte-for-byte in the shipped probe) -- used
directly, no rebuild.

**Collection:** `collect_debug_games.py <probe> boss 6` -- 6/6 games returned cleanly, no HTTP
422, no retry needed.

### Per-game numbers

| gameId | result | final turn | my wood | boss wood | wood delta @final | max seeds (tent) | flaps (final) | banana@t150 | banana@t~300/final |
|---|---|---|---|---|---|---|---|---|---|
| 895437502 | L | 300 | 66 | 84 | -18 | 7 | 9 | 7 | 7 |
| 895437524 | L | 300 | 36 | 59 | -23 | 4 | 3 | 4 | 4 |
| 895437570 | L | 300 | 30 | 56 | -26 | 2 | 8 | 2 | 2 |
| 895437583 | W | 300 | 59 | 49 | +10 | 7 | 6 | 7 | 7 |
| 895437610 | L | 300 | 48 | 62 | -14 | 5 | 2 | 5 | 5 |
| 895437624 | W | 174 (natural early end -- `trees=0` from t170 on, both sides fully deforested the map; clean `@TFSUM`/`@TFD` progression to the last frame, no panic/error string anywhere in the `.raw`) | 33 | 30 | +3 | 3 | 2 | 1 | 0 |

Wins 2/6 (33%, vs the standing ~14% baseline win rate) -- context only, not a gate criterion.

### Readout 1 -- CRATER CHECK (the gate)

- avg final wood (ours) = **45.3** -- inside the era 45-52 band, clears the ≥40 floor. **PASS**
- min final wood = **30** (game 895437570) -- clears the >25 floor with margin. **PASS**
- avg wood delta @ final turn (t300 or the natural early-end turn) = **-11.3** -- clears the
  ≥ -14 floor (also better than the ramp.py-printed -15.3 historical baseline). **PASS**
- crashes: **0/6** -- no panic/error/backtrace string in any of the 6 `.raw` files; all 6
  headers show plausible non-degenerate `scores` pairs. **PASS**

**All four hold -> readout 1 PASSES.**

### Readout 2 -- BANANA FLOW (diagnostic, non-gating)

`seeds=` (tent stock, `state.my_inventory[BANANA]`) does sit **above** the historical era
norm of flat-0 in all 6 games (max seeds per game: **7, 4, 2, 7, 5, 3** -- avg 4.7, never 0).
However the shape is a **plateau, not a climb**: in 5/6 games the value is set by t5 and then
perfectly flat for the entire rest of the game (295 turns, unchanged to the digit -- see the
per-game seeds series pulled from `@TFFARM`); only the one early-ending game
(895437624) shows the tent stock draining (3 -> 2 -> 1 -> 0 across t140-155) rather than
climbing. `@TFD` banana inventory at t150 / t~300(-or-final) matches the `@TFFARM` seeds
reading exactly at every checked game (7/7, 4/4, 2/2, 7/7, 5/5, 1/0) -- the two telemetry
sources agree. Read: tree-first harvesting front-loads a small persistent banked buffer early
and then goes quiet (consistent with the farm hitting `farm_cap` almost immediately, after
which the whole printer band -- including the new band-52 push -- stops firing for the rest
of the game); it is not compounding a growing tent hoard over time. Not a crater signal either
way; flagged for the analyst as a shape worth understanding, not a defect.

### Readout 3 -- Flaps

Final `flaps=` value per game: 9, 3, 8, 2, 6, 2 (order matches the table above: 895437502,
895437524, 895437570, 895437583, 895437610, 895437624) -- all ≤15. **6/6 ≥ the required 5/6.
PASS.**

### Verdict: **PASS**

No crater signature. All three readouts clear their bars; the diagnostic banana-flow shape
(early plateau, not a climb) is worth a follow-up note for the analyst but does not change the
gate outcome. No field games run (out of scope for this reduced probe). Recommend proceeding
to the arena-runner step per the existing queue position (`docs/arena-queue.md` #1).
