# FellForWood Mission (v1.60.0-fellmission) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Replace the chopper's weighted fell bands with one explicit, committed FellForWood
mission that picks the most wood-efficient reachable tree and fells it fully — fixing the
"wrong-tree" bug (chopper sat on a health-20 apple 9 turns for 0 wood) with straight reasoning,
not a weight tweak. First increment of the intent-driven mission layer (spec:
`docs/superpowers/specs/2026-07-10-intent-missions-design.md`).

**Architecture:** New `rust/src/botmain/missions.rs` computes the chopper's committed fell target
by explicit efficiency `wood/(travel+chops)`; `decide_elite` gives the chopper its mission
command and excludes it from the band system; all other trolls stay on the proven bands; the
joint move solver (`motion::solve_moves`) still resolves all movement. Ships as candidate
v1.60.0-fellmission on the v1.59.0-ringfix3 champion base.

**Tech Stack:** Rust (rust/), cargo test --release; submission via tools/bundle.py → minify.py;
python via `uv run --no-sync python`.

## Global Constraints
- Base = v1.59.0-ringfix3 (the champion). Verify `grep 'const VERSION' rust/src/botmain.rs` =
  "1.59.0-ringfix3" before starting; bump to "1.60.0-fellmission" at the end.
- Preserve champion consts: GE_CHOP_R=5, RACE_SHARE_PEN=2, DENY_W=0, STICKY=6, GE_MAX_TROLLS=2,
  GE_FARM_R=2, farm_fell=2.
- Determinism: every candidate/target selection sorts canonically (by a total key incl. the cell);
  NO HashSet iteration into any decision (recurring hazard in this codebase).
- Only the CHOPPER (chop_power >= 2) is moved to the mission. All non-chopper trolls' behavior
  MUST be unchanged (the +1.7 economy stays on the bands). A gate check confirms this.
- This CHANGES chopper behavior → no champion stream-equality expected; self-determinism
  (bot vs bot) must stay EQUAL.
- Existing types (from state.rs): `type Cell = (i32,i32)`; `Tree { tree_type:String, x,y,size,
  health,fruits,cooldown }` with `.pos()->Cell`; `Troll { id,x,y,movement_speed,carry_capacity,
  harvest_power,chop_power,carry:[i32;6] }` with `.pos()`, `.free_capacity()`; helpers
  `bfs_distances(&walkable,&[Cell])->HashMap<Cell,i32>`, `manhattan(a,b)`, `ortho_neighbors(cell)`.
  Resource index consts: BANANA=3, WOOD=5 (state.rs).

---

### Task 1: Extract `race` to a reusable free function (behavior-preserving)

**Files:**
- Modify: `rust/src/botmain/planner.rs` (the `let race = |pc, our_eta| {...}` closure at ~:263
  and its 4 call sites at ~:426,460,745,776)

**Interfaces:**
- Produces: `pub(crate) fn race(state: &State, pc: Cell, our_eta: i64) -> Option<i64>` — returns
  `None` = doomed (enemy chopper on `pc` fells it before `our_eta`); `Some(0)` = uncontested;
  `Some(RACE_SHARE_PEN)` = joinable contested. Consumed by Task 2 (missions.rs) and the existing
  candidates() call sites.

- [ ] **Step 1:** Move the closure body verbatim into a module-level
  `pub(crate) fn race(state: &State, pc: Cell, our_eta: i64) -> Option<i64>` (it already only
  reads `state`, `RACE_SHARE_PEN`). Replace the 4 call sites `race(pc, steps)` →
  `race(state, pc, steps)`. Delete the closure.
- [ ] **Step 2:** `cd rust && cargo test --release` — all existing tests green (behavior
  unchanged; the closure only captured `state`).
- [ ] **Step 3:** Self-determinism equality: `./target/release/equality target/release/bot
  target/release/bot 8 300 target/release/bot` → EQUAL. (This refactor is pure extraction.)
- [ ] **Step 4:** Commit: `refactor(planner): extract race closure → pub(crate) fn race(state,pc,eta) (reusable by missions)`.

---

### Task 2: `missions.rs` — FellForWood target selection (the wrong-tree fix, pure)

**Files:**
- Create: `rust/src/botmain/missions.rs`
- Modify: `rust/src/botmain.rs` (add `mod missions;` near the other `mod` lines)
- Test: `rust/tests/fellmission.rs`

**Interfaces:**
- Consumes: `planner::race`, `state::{bfs_distances, manhattan}`, Tree/Troll fields.
- Produces: `pub fn fell_target(state: &State, chopper: &Troll) -> Option<Cell>` — the most
  wood-efficient reachable fellable tree not doomed by race(); `None` if none.

- [ ] **Step 1: Write the failing test** (`rust/tests/fellmission.rs`) on the clipboard
  geometry: chopper at (6,2) chop_power 2; trees APPLE (7,1) health 20 size 4, LEMON (7,0)
  health 12 size 4, BANANA (9,5) health 6 size 4 (farther). Assert `fell_target` returns
  `(9,5)` (banana: eff 4/(4+3)=0.57) over LEMON (4/(3+6)=0.44) and APPLE (4/(2+10)=0.33) — i.e.
  the SOFT tree wins even from farther, the tanky apple is never chosen.
```rust
#[test]
fn fellmission_picks_wood_efficient_tree_not_nearest_tank() {
    let st = /* build State: walkable rect, chopper (6,2) chop=2, the 3 trees above */;
    assert_eq!(missions::fell_target(&st, &st.my_trolls[0]), Some((9,5)));
}
```
- [ ] **Step 2:** Run: `cargo test --release --test fellmission` → FAIL (fell_target undefined).
- [ ] **Step 3: Implement** `fell_target`:
```rust
pub fn fell_target(state: &State, u: &Troll) -> Option<Cell> {
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed.max(1);
    let cp = u.chop_power.max(1);
    let mut best: Option<(i64 /*eff_num scaled*/, Cell)> = None;
    let mut cands: Vec<(i64, Cell)> = Vec::new();      // (-efficiency_scaled, cell) canonical
    for t in &state.trees {
        let pc = t.pos();
        let steps = match d.get(&pc) { Some(&s) => s as i64, None => continue }; // reachable
        let chops = ((t.health + cp - 1) / cp) as i64;
        if chops <= 0 { continue; }
        // race guard: skip trees an enemy fells before our arrival
        let our_eta = (steps + ms as i64 - 1) / ms as i64;
        if planner::race(state, pc, our_eta).is_none() { continue; }
        // efficiency = wood_yield / (travel + chops); wood_yield = size (fell wood ~ size)
        // scale to integer: eff_scaled = size*1000 / (steps+chops) ; higher = better
        let eff = (t.size as i64 * 1000) / (steps + chops).max(1);
        cands.push((-eff, pc)); // negate so smaller = better for canonical sort
    }
    cands.sort();                    // canonical: best efficiency, then cell (deterministic)
    cands.first().map(|&(_, c)| c)
}
```
- [ ] **Step 4:** Run `cargo test --release --test fellmission` → PASS. Add a second test
  `fellmission_skips_doomed_tree` (enemy chopper on the banana with health low enough that
  `their_turns <= our_eta`) → asserts the doomed tree is skipped, the lemon returned.
- [ ] **Step 5:** Commit: `feat(missions): fell_target — explicit wood-efficiency tree choice (fixes wrong-tree)`.

---

### Task 3: Mission commitment — persist the target, re-plan only on Done/Invalidated

**Files:**
- Modify: `rust/src/botmain/missions.rs`
- Test: `rust/tests/fellmission.rs`

**Interfaces:**
- Produces: `pub fn reset()` (turn-1 clear); `pub fn chopper_target(state:&State, u:&Troll) ->
  Option<Cell>` — returns the COMMITTED target (kept across turns) unless it is Done (tree gone)
  or Invalidated (race lost / unreachable), else a fresh `fell_target`. Uses a thread_local
  `COMMITTED: RefCell<HashMap<i32,Cell>>` (pattern: planner.rs LAST_TGT).

- [ ] **Step 1: Write the failing test** — commit-no-abandon: turn A `chopper_target` picks tree
  X; then a NEARER tree Y appears; assert turn B still returns X (committed), not Y. Then remove
  X from state.trees; assert turn C re-plans to Y.
- [ ] **Step 2:** Run → FAIL (chopper_target undefined).
- [ ] **Step 3: Implement** `chopper_target`: if COMMITTED holds a cell C for `u.id` AND a tree
  still stands at C AND C is reachable (`bfs_distances` contains C) AND `race(state,C,eta)` is
  not None → return C. Else compute `fell_target`, store it in COMMITTED, return it. `reset()`
  clears COMMITTED. Canonical/deterministic (no HashSet iteration into the decision).
- [ ] **Step 4:** Run → PASS. Wire `missions::reset()` into `decide_elite`'s turn-1 reset block
  (alongside `planner::reset()`).
- [ ] **Step 5:** Commit: `feat(missions): commitment — chopper stays on its fell target until done/invalidated (no abandon/backtrack)`.

---

### Task 4: Wire the chopper's mission into decide_elite; exclude it from the bands; joint-solve

**Files:**
- Modify: `rust/src/botmain.rs` (`decide_elite`, ~:124 where `assign_resolved` is called)

**Interfaces:**
- Consumes: `missions::chopper_target`, `motion::solve_moves`, `planner::assign_resolved`.

- [ ] **Step 1: Write the failing test** (`rust/tests/fellmission.rs`,
  `fellmission_chopper_uses_mission_starter_unchanged`): a 2-troll state (chopper + starter);
  assert (a) the chopper's emitted command is `CHOP` (if on the target tree) or a `MOVE` toward
  `chopper_target`, NOT whatever the bands would have given; (b) the STARTER's command is
  byte-identical to a baseline run with only the starter through `assign_resolved`.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** in `decide_elite`, replacing the single `assign_resolved` call:
```rust
let chopper = my.iter().find(|t| t.chop_power >= 2).map(|t| t.id);
// non-chopper trolls flow through the proven band system
let others: Vec<Troll> = my.iter().filter(|t| Some(t.id) != chopper).cloned().collect();
let mut cmd_by_id = planner::assign_resolved(state, &plan, &others);
// chopper: explicit FellForWood mission
if let Some(cid) = chopper {
    let u = my.iter().find(|t| t.id == cid).unwrap();
    let cmd = match missions::chopper_target(state, u) {
        Some(tc) if tc == u.pos() => format!("CHOP {}", cid),          // on the tree → fell
        Some(tc) => format!("MOVE {} {} {}", cid, tc.0, tc.1),         // route (solver refines)
        None => format!("WAIT {}", cid),                               // no reachable tree
    };
    cmd_by_id.insert(cid, cmd);
}
// joint move solve over ALL intents (chopper + others) — keeps shuffle-invariant motion
let intents = motion::move_intents(&cmd_by_id);           // reuse existing extractor
let landing = motion::solve_moves(state, &my, &intents);
motion::pin_landing(&my, &mut cmd_by_id, landing);        // reuse existing pinner
```
  (If `move_intents`/`pin_landing` are private to planner, make them `pub(crate)` in motion.rs —
  they already exist there per the R6 solver; verify names and visibility.)
- [ ] **Step 4:** Run the test → PASS. Then `cargo test --release` full suite green.
- [ ] **Step 5:** Self-determinism equality (8 seeds) → EQUAL. Commit:
  `feat(botmain): chopper runs the FellForWood mission, excluded from fell bands; joint-solve preserved`.

---

### Task 5: @TFMISSION telemetry (the readable-decision payoff) + VERSION + freeze

**Files:**
- Modify: `rust/src/botmain.rs` (DEBUG block in decide_elite), `rust/src/botmain.rs` VERSION
- Artifacts: `cgauto/submissions/v1.60.0-fellmission.{rs,min.rs}` + `data/candidates/v1.60.0-fellmission/`

**Interfaces:** none (telemetry + build).

- [ ] **Step 1:** In `decide_elite` under `if DEBUG`, emit per chopper:
  `eprintln!("@TFMISSION t={} id={} kind=FellForWood target={:?} chops={}", turn, cid, tc, chops_left);`
  (compute chops_left = ceil(health/chop_power) of the target tree, or -1 if none).
- [ ] **Step 2:** Bump `const VERSION` to `"1.60.0-fellmission"`.
- [ ] **Step 3:** Build gates: `uv run --no-sync python tools/bundle.py src/botmain.rs
  ../target/refactor/b.rs` → rustc --edition 2021 -O compiles → `tools/minify.py` < 100000 B →
  compile the minified copy. Freeze to `cgauto/submissions/` and `data/candidates/`; build the
  DEBUG probe (sed DEBUG false→true → minify → compile).
- [ ] **Step 4:** Commit: `chore(fellmission): @TFMISSION telemetry + VERSION 1.60.0 + freeze artifacts`.

---

### Task 6: Gate — verify the fix, no economy regression (paired vs ringfix3)

**Files:** `data/candidates/v1.60.0-fellmission/report.md` (append)

- [ ] **Step 1:** Play >=6 vs boss + >=6 vs Crouistiti (6479836) with the DEBUG probe, AND
  re-measure v1.59.0-ringfix3 on the SAME batch (paired; run sequentially — concurrent play
  triggers HTTP 422s). Report per pair: (a) wood avg (must be ≥ ringfix3 — the conversion
  thesis: efficient felling = more wood/chop); (b) @TFMISSION shows the chopper picking
  soft/efficient trees and felling them fully (no 9-turn apple sit); (c) win-rate.
- [ ] **Step 2:** If wood ≥ ringfix3 and no crater → PASS, hand to the arena-runner (chained on
  the live ringfix3 bracket; KEEP if delta ≥ +0.5, per policy v2). If wood DROPS → the chopper
  mission is losing productive felling the bands were doing — flag before any arena run.
- [ ] **Step 3:** Append the gate verdict + numbers to the report; commit.

---

## Self-Review
- **Spec coverage:** FellForWood mission (Task 2), commitment (Task 3), keep-motion-solver
  (Task 4 joint-solve), telemetry (Task 5), preserve-race-win (Task 1 reuse), gate-vs-champion
  (Task 6). The other missions (Bank/BuildRing/TrainTroll/HarvestFruit) are OUT of this
  increment per the incremental build path — later plans.
- **Placeholder scan:** the Task-2/3 test State construction is sketched (`/* build State */`) —
  the implementer must fill it from an existing test's fixture (see rust/tests/planner_tasks.rs
  or ringfix3.rs for the State-builder pattern); flagged, not a silent TODO.
- **Type consistency:** `fell_target(state,u)` (T2) → `chopper_target(state,u)` wraps it (T3) →
  `decide_elite` calls `chopper_target` (T4). `race(state,pc,eta)` (T1) used by T2. Consistent.
