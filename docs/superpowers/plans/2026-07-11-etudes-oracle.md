# Etudes Forced-Outcome Oracle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** A library that takes a small Troll Farm position and PROVES who wins under ideal play
(forced outcome), reusing the deterministic game engine — the substrate for the etudes database
+ viewer (later sub-projects). Spec: `docs/superpowers/specs/2026-07-11-etudes-oracle-design.md`.

**Architecture:** New `rust/src/etudes/` module: `situation.rs` (a serializable position + horizon),
`actions.rs` (pruned sensible per-troll commands), `oracle.rs` (sound informed-minimax forced-win
prover with alpha-beta + transposition table + node budget over `game::engine::step`). Depends
only on `game::` (state + engine), never on `botmain`.

**Tech Stack:** Rust in the existing crate (`rust/`), `cargo test --release`.

## Global Constraints
- New module under `rust/src/etudes/`; add `pub mod etudes;` to `rust/src/lib.rs`. No dependency
  on `botmain`.
- Reuse existing `game::state::{GameState, Unit, Plant, from_ascii}` and
  `game::engine::{step, recompute_scores, next_cell}`. Do NOT reimplement game rules.
- Forced-outcome ONLY: verdict is `ForcedWin{side}` (a side guarantees score-diff > 0 vs any
  opponent play), else `Unresolved`, else `TooLarge`. Outcome metric = `scores[X]-scores[Y]` at
  the horizon (scores = fruit + 4·wood via `recompute_scores`).
- Determinism: NO HashSet-iteration into any decision; all action/state ordering canonical
  (sorted). `forced_verdict` is a pure function of the `Situation`.
- Engine facts (verified): `GameState{width,height,walkable:HashSet<Cell>,shacks:[Cell;2],
  inventories:[[i32;6];2],units:Vec<Unit>,plants:Vec<Plant>,scores:[i32;2],turn:i32,next_id:i32,
  iron:HashSet<Cell>,water:HashSet<Cell>}` is `Clone`. `Unit{id,player,x,y,ms,cc,hp,chop,
  carry:[i32;6]}` with `.pos()/.free()`. `Plant{plant_type:String,x,y,size,health,fruits,
  cooldown}` with `.pos()`. `Cell=(i32,i32)`. Resource idx: PLUM0 LEMON1 APPLE2 BANANA3 IRON4
  WOOD5. `step(&mut game, cmds0:&[String], cmds1:&[String])` advances one turn. Command strings:
  `WAIT`, `MOVE <id> <x> <y>`, `CHOP <id>`, `HARVEST <id>`, `PLANT <id> <TYPE>`, `MINE <id>`,
  `DROP <id>`, `PICK <id> <ITEM>`, `TRAIN <ms> <cc> <hp> <chop>` (parse_cmds in engine.rs:622).

---

### Task 1: `situation.rs` — Situation type + text round-trip serialization

**Files:**
- Create: `rust/src/etudes/situation.rs`, `rust/src/etudes/mod.rs`
- Modify: `rust/src/lib.rs` (add `pub mod etudes;`)
- Test: `rust/tests/etudes.rs`

**Interfaces:**
- Produces: `pub struct Situation { pub state: game::state::GameState, pub horizon: u32,
  pub prove_side: Option<usize> }`; `pub fn to_text(&Situation) -> String`;
  `pub fn from_text(&str) -> Situation`.

- [ ] **Step 1: Write the failing test** in `rust/tests/etudes.rs`:
```rust
use troll_farm::etudes::situation::{Situation, to_text, from_text};
#[test]
fn situation_roundtrip() {
    let text = "\
MAP 5 3
.0..1
.....
..+..
INV0 0 0 0 2 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 3 1 2 4 0 0
TURN 10
SCORES 0 0
HORIZON 6
PROVE -";
    let s = from_text(text);
    assert_eq!(s.horizon, 6);
    assert_eq!(s.prove_side, None);
    assert_eq!(s.state.units.len(), 1);
    assert_eq!(s.state.plants.len(), 1);
    assert_eq!(s.state.units[0].chop, 2);
    // round-trip: parsing the re-serialized text yields the same fields
    let s2 = from_text(&to_text(&s));
    assert_eq!(s2.state.units, s.state.units);
    assert_eq!(s2.state.plants, s.state.plants);
    assert_eq!(s2.state.inventories, s.state.inventories);
    assert_eq!(s2.state.turn, s.state.turn);
    assert_eq!(s2.horizon, s.horizon);
}
```
- [ ] **Step 2:** `cd rust && cargo test --release --test etudes situation_roundtrip` → FAIL
  (module/fns undefined). (Add `#[derive(PartialEq)]` to `Unit`/`Plant` in state.rs if missing —
  the test compares them; they already derive Clone/Debug, add PartialEq.)
- [ ] **Step 3: Implement** `situation.rs`:
  - `from_text`: split into lines. The `MAP w h` + the next `h` grid rows → build terrain via
    `game::state::from_ascii(&rows)` (it sets walkable/shacks/iron/water). THEN clear
    `state.units`/`state.plants` and set them + `inventories`/`turn`/`scores` from the explicit
    `INV0/INV1/UNIT/PLANT/TURN/SCORES` lines; set `horizon` from `HORIZON`; `prove_side` from
    `PROVE` (`-`→None, `0`/`1`→Some). UNIT fields in order id,player,x,y,ms,cc,hp,chop,carry[6];
    PLANT fields type,x,y,size,health,fruits,cooldown.
  - `to_text`: inverse — emit `MAP`, the grid (reconstruct rows from walkable/shacks/iron/water:
    `0`/`1` at shacks, `+` at iron, `~` at water, `#` for non-walkable-non-water-non-iron, `.`
    for walkable), then INV/UNIT/PLANT/TURN/SCORES/HORIZON/PROVE. Canonical order: units sorted
    by id, plants sorted by (x,y).
  - `mod.rs`: `pub mod situation; pub mod actions; pub mod oracle;` (actions/oracle added later —
    for Task 1 just `pub mod situation;`, extend in Tasks 2/3).
- [ ] **Step 4:** `cargo test --release --test etudes situation_roundtrip` → PASS.
- [ ] **Step 5: Commit** `feat(etudes): Situation type + text round-trip serialization`.

---

### Task 2: `actions.rs` — pruned sensible per-troll commands

**Files:**
- Create: `rust/src/etudes/actions.rs`
- Modify: `rust/src/etudes/mod.rs` (`pub mod actions;`)
- Test: `rust/tests/etudes.rs`

**Interfaces:**
- Consumes: `game::state::{GameState, Unit}`, `game::engine::next_cell`.
- Produces: `pub fn troll_actions(state:&GameState, u:&Unit) -> Vec<String>`;
  `pub fn joint_actions(state:&GameState, player:usize) -> Vec<Vec<String>>` (each element = one
  candidate command-list for ALL of that player's units this turn).

- [ ] **Step 1: Write the failing test**:
```rust
use troll_farm::etudes::actions::{troll_actions, joint_actions};
#[test]
fn actions_pruned_and_canonical() {
    let s = from_text("\
MAP 5 3
.0..1
.....
..B..
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 4
PROVE -").state;
    let acts = troll_actions(&s, &s.units[0]);
    // sensible only: WAIT + a MOVE toward the tree + a MOVE toward the shack; NOT 8 blind dirs;
    // no CHOP (not on the tree). canonical (sorted, deduped).
    assert!(acts.contains(&"WAIT 0".to_string()));
    assert!(acts.iter().any(|a| a.starts_with("MOVE 0 ")));
    assert!(!acts.contains(&"CHOP 0".to_string())); // unit not on a tree
    assert_eq!(acts, { let mut v=acts.clone(); v.sort(); v.dedup(); v }); // canonical
    // one-unit player → joint == each single action wrapped
    let j = joint_actions(&s, 0);
    assert_eq!(j.len(), acts.len());
    assert!(j.iter().all(|c| c.len()==1));
}
```
- [ ] **Step 2:** run → FAIL (undefined).
- [ ] **Step 3: Implement**:
  - `troll_actions`: build the candidate set (as a `BTreeSet<String>` for canonical order):
    always `WAIT <id>`. For each PLANT tree and the shack `state.shacks[u.player as usize]` and
    each IRON cell, if `u.pos() != target` emit `MOVE <id> <tx> <ty>` (the engine's `next_cell`
    resolves the path; we pass the final target, one MOVE per distinct target). If `u.pos()`
    equals a tree cell: `CHOP <id>` (if `u.chop>0`) and `HARVEST <id>` (if `u.hp>0 && u.free()>0
    && that tree.fruits>0`). If adjacent-to-shack (manhattan ≤1) and `u.free()>0` and inventory
    has a plantable item: `PICK <id> BANANA` (when tent has banana); if carrying: `DROP <id>`.
    If on a walkable empty cell with a carried BANANA: `PLANT <id> BANANA`. If adjacent to iron:
    `MINE <id>`. Keep it to the sensible set — do NOT emit all 8 compass moves. Return the
    BTreeSet as a sorted `Vec<String>`.
  - `joint_actions`: for the player's units (sorted by id), take the cartesian product of each
    unit's `troll_actions`. For 1 unit → wrap each action in a 1-element Vec. Bound: if the
    product exceeds a cap (e.g. 64), that's fine here (this sub-project targets 1 unit/side); the
    oracle's node budget (Task 3) handles blow-ups. Canonical: iterate units in id order,
    actions in sorted order.
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(etudes): pruned sensible troll_actions + joint_actions`.

---

### Task 3: `oracle.rs` — forced-win verdict via informed-minimax (no proof yet)

**Files:**
- Create: `rust/src/etudes/oracle.rs`
- Modify: `rust/src/etudes/mod.rs` (`pub mod oracle;`)
- Test: `rust/tests/etudes.rs`

**Interfaces:**
- Consumes: `game::{state::GameState, engine::{step, recompute_scores}}`, `situation::Situation`,
  `actions::joint_actions`.
- Produces: `pub enum Verdict { ForcedWin{side:usize}, Unresolved, TooLarge }` (proof added in
  Task 4 — for now `ForcedWin` has no proof field); `pub fn forced_verdict(&Situation)->Verdict`.

- [ ] **Step 1: Write the failing tests**:
```rust
use troll_farm::etudes::oracle::{forced_verdict, Verdict};
#[test]
fn oracle_forced_win_by_felling() {
    // our troll (chop 2) starts ON a size-2 banana (health 4 = 2 chops); opponent has no unit.
    // H=4 is enough to CHOP,CHOP (fell → +2 wood carried) — score-diff > 0 forced.
    let s = from_text("\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0");
    assert!(matches!(forced_verdict(&s), Verdict::ForcedWin{side:0}));
}
#[test]
fn oracle_unresolved_or_symmetric() {
    // no reachable resource for either side in H turns → nobody forces a positive diff.
    let s = from_text("\
MAP 5 3
.0..1
.....
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
UNIT 3 1 3 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 2
PROVE -");
    assert!(matches!(forced_verdict(&s), Verdict::Unresolved));
}
```
- [ ] **Step 2:** run → FAIL (undefined).
- [ ] **Step 3: Implement** `oracle.rs`:
```rust
use std::collections::HashMap;
use crate::game::{self, state::GameState};
use super::situation::Situation;
use super::actions::joint_actions;

const NODE_BUDGET: u64 = 5_000_000;

#[derive(Debug, PartialEq)]
pub enum Verdict { ForcedWin { side: usize }, Unresolved, TooLarge }

// X's guaranteed score-diff at the horizon when Y is INFORMED (sees X's move and best-responds).
// This lower-bounds X's true simultaneous security level, so value>0 ⇒ genuine forced win.
// Returns None if the node budget is exhausted.
fn informed_minimax(st:&GameState, x:usize, depth:u32,
                    memo:&mut HashMap<(u64,u32,usize),i32>, budget:&mut u64) -> Option<i32> {
    if depth == 0 {
        let mut s = st.clone(); game::engine::recompute_scores(&mut s);
        return Some(s.scores[x] - s.scores[1-x]);
    }
    let key = (canonical_hash(st), depth, x);
    if let Some(&v) = memo.get(&key) { return Some(v); }
    let (y, xm, ym) = (1-x, joint_actions(st, x), joint_actions(st, y_of(x)));
    let mut best_x = i32::MIN;                      // alpha
    for xc in &xm {
        let mut worst = i32::MAX;                   // Y minimizes
        for yc in &ym {
            if *budget == 0 { return None; } *budget -= 1;
            let mut s = st.clone();
            let (c0,c1) = if x==0 {(xc.clone(),yc.clone())} else {(yc.clone(),xc.clone())};
            game::engine::step(&mut s, &c0, &c1);
            let v = informed_minimax(&s, x, depth-1, memo, budget)?;
            if v < worst { worst = v; }
            if worst <= best_x { break; }           // alpha-beta prune
        }
        if worst > best_x { best_x = worst; }
    }
    memo.insert(key, best_x);
    Some(best_x)
}
fn y_of(x:usize)->usize{1-x}

// Canonical, order-independent hash of the DYNAMIC state (terrain/map is fixed within an etude).
fn canonical_hash(st:&GameState) -> u64 {
    use std::hash::{Hash,Hasher}; use std::collections::hash_map::DefaultHasher;
    let mut u:Vec<_> = st.units.iter().map(|z|(z.id,z.player,z.x,z.y,z.carry)).collect(); u.sort();
    let mut p:Vec<_> = st.plants.iter().map(|z|(z.x,z.y,z.size,z.health,z.fruits,z.cooldown)).collect(); p.sort();
    let mut h = DefaultHasher::new();
    (u, p, st.inventories, st.turn).hash(&mut h); h.finish()
}

pub fn forced_verdict(sit:&Situation) -> Verdict {
    let sides:Vec<usize> = match sit.prove_side { Some(p)=>vec![p], None=>vec![0,1] };
    for x in sides {
        let mut memo = HashMap::new(); let mut budget = NODE_BUDGET;
        match informed_minimax(&sit.state, x, sit.horizon, &mut memo, &mut budget) {
            None => return Verdict::TooLarge,
            Some(v) if v > 0 => return Verdict::ForcedWin{ side:x },
            _ => {}
        }
    }
    Verdict::Unresolved
}
```
  (Note: `Unit`/`Plant` `carry`/fields must be `Hash+Ord` for the tuples — `[i32;6]` and i32 are;
  `plant_type` String isn't in the hash tuple, fine since a cell hosts one plant.)
- [ ] **Step 4:** run both tests → PASS. Also add `oracle_toolarge` (a horizon/position that
  exceeds `NODE_BUDGET` — e.g. 2 units/side, H=8, open map — asserting `TooLarge`, verifying it
  RETURNS rather than hangs; keep the fixture minimal so the budget trips fast).
- [ ] **Step 5: Commit** `feat(etudes): forced_verdict oracle (informed-minimax + alpha-beta + transposition + node budget)`.

---

### Task 4: proof extraction + `replay_proof` validation

**Files:**
- Modify: `rust/src/etudes/oracle.rs`
- Test: `rust/tests/etudes.rs`

**Interfaces:**
- Produces: `pub struct Proof { pub line: Vec<(String, i32)> }` (the forcing side's chosen joint
  command at each ply on the principal line + the resulting min score-diff), attached to
  `ForcedWin{side, proof}`; `pub fn replay_proof(&Situation, &Verdict) -> bool` (re-runs the
  forcing side's committed actions against a BRUTE-FORCE opponent and asserts every leaf has
  score-diff > 0).

- [ ] **Step 1: Write the failing test**:
```rust
#[test]
fn oracle_proof_replays_valid() {
    let s = from_text(/* the oracle_forced_win_by_felling fixture */ );
    let v = forced_verdict(&s);
    assert!(matches!(v, Verdict::ForcedWin{..}));
    assert!(troll_farm::etudes::oracle::replay_proof(&s, &v));  // proof genuinely holds
}
```
- [ ] **Step 2:** run → FAIL (Proof/replay_proof undefined; `ForcedWin` has no proof field).
- [ ] **Step 3: Implement**: extend `informed_minimax` to also return the chosen X joint-action at
  each node on the achieving line (or add a thin second pass `extract_line` that, given the solved
  memo/value, walks the principal variation: at each ply pick X's argmax action and Y's argmin
  response, recording X's action + the resulting value until depth 0). Attach as `Proof`.
  `replay_proof`: from the situation, at each ply apply the proof's X action and ENUMERATE every Y
  `joint_actions` response via `step`, recursing; assert the horizon score-diff > 0 on EVERY
  branch (this re-verifies the guarantee independently of the search, catching any bug in the
  minimax). Return false if any branch is ≤ 0.
- [ ] **Step 4:** run → PASS. Confirm `oracle_forced_win_by_felling`/`oracle_unresolved` still
  pass with the `ForcedWin{side, proof}` shape.
- [ ] **Step 5: Commit** `feat(etudes): forcing-line proof + replay_proof independent validation`.

---

### Task 5: determinism + full-suite gate

**Files:** Test: `rust/tests/etudes.rs`

- [ ] **Step 1:** add `oracle_deterministic`: call `forced_verdict` twice on the same situation,
  assert identical `Verdict` (and identical proof line) — guards the canonical-order/no-HashSet-leak
  requirement.
- [ ] **Step 2:** `cargo test --release` → FULL workspace suite green (etudes tests + all existing
  bot tests unaffected — the etudes module is isolated, `botmain` untouched).
- [ ] **Step 3: Commit** `test(etudes): determinism + full-suite green`.

---

## Self-Review
- **Spec coverage:** situation format + round-trip (T1); pruned actions (T2); informed-minimax
  forced-win oracle + alpha-beta + transposition + TooLarge budget (T3); proof + replay validation
  (T4); determinism (T5). Verdict/Unresolved/TooLarge, forced-only, score-diff metric, engine
  reuse, no-botmain-dep — all covered. DB/viewer/CLI explicitly deferred (spec scope).
- **Placeholder scan:** none — every code step has real code. The `extract_line` in T4 is
  sketched two ways (extend minimax OR second pass); the implementer picks one — flagged, not a
  silent TODO.
- **Type consistency:** `Situation{state,horizon,prove_side}` (T1) consumed by `forced_verdict`
  (T3); `joint_actions` (T2) consumed by `informed_minimax` (T3); `Verdict::ForcedWin` gains
  `proof:Proof` in T4 (T3 tests use `matches!(.., ForcedWin{side:0})` which still matches with
  the added field via `ForcedWin{side:0, ..}` — update the T3 test asserts to `{side:0, ..}` when
  T4 lands). Consistent.
