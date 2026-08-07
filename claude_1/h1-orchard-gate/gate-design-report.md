# Orchard opportunity-cost activation gate — design report

Target program: round-36 minified bot, one line, 55,799 bytes.

**Provenance note (important).** The path given for the minified file
(`/home/tarstars/prj/troll_farm-claude_1/claude_1/e7a-incremental-simplification/candidate-r36-delete-orphaned-carry-total.rs`)
does not exist on disk; that directory ends at r28. The actual 55,799-byte one-line r36 program is in git:

- repo: `/home/tarstars/prj/troll_farm-claude_1`
- blob: `68b07054:claude_1/r36-submission/candidate-agent6553250-e7a-r36-simplified.min.rs` (also referenced by `c61bc8eb`)
- extracted working copy used for all anchor verification below:
  `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/h1/r36-min.rs`
- sha256 `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`, `wc -cl` = 1 line, 55,799 bytes — matches the task's stated size exactly.

All anchors below were byte-verified against this file, and the full patched program was compiled with
`rustc --edition 2021 -O` (exit 0, zero errors, no new warnings — the single pre-existing
"unnecessary parentheses around `if` condition" warning is present in the unpatched baseline too).
Patched size: 57,592 bytes (+1,793).

Readable reference: `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/h1/e7a-r36-readable.rs` (line numbers below refer to it).

---

## A. Value inventory at the activation decision point

Decision point (readable line 2452, inside `SecureOrchardBot::commands`, `&mut self`):

```rust
if checkpoint && has_second && self.can_activate(view, starter, &geometry) {
    self.phase = OrchardPhase::CarryingSeed;
```

Context guaranteed at this point:

| Fact | Source (readable file) |
|---|---|
| `view.turn <= 100` | guard at line 2448 (`view.turn > 100` → Abandoned before the check) |
| starter is empty-handed on a home door (`checkpoint = empty_on_door`) | lines 2444–2446; so `starter.free_capacity() == starter.stats.carry_capacity` |
| two friendly units exist (`has_second`) | line 2443 |
| mother reachable from starter, mother cell empty, no other unit on it | `can_activate`, lines 2259–2265 |
| nearest armed enemy is > 8 travel-turns from the mother | `Self::enemy_eta`, lines 2164–2176, used at 2266 |
| `geometry` is an owned clone (`self.geometry.clone()`, line 2428); `starter: &Unit` borrows `view`, not `self` | lines 2428–2432 |

### Orchard side

| Quantity | How to compute | Source |
|---|---|---:|
| `turns_left` | `TOTAL_TURNS - view.turn + 1` (`TOTAL_TURNS = 300`) | rules line 138; same expression used at 816, 1649, 1789, 2101 |
| travel to mother | `ceil_div(bfs_distances(&view.walkable,&[starter.cell])[&geometry.mother], starter.stats.movement_speed)` | `bfs_distances` 220, `ceil_div` 514 (`ceil_div` returns 10_000 on non-positive divisor — no div-by-zero) |
| apple growth cadence at the mother | `effective_cooldown(PlantKind::Apple, true) = 9 - 7 = 2` | `plant_cooldown` 140–147, `water_boost` 148–155, `effective_cooldown` 167–169. `near_water = true` is guaranteed by construction: `initialize` only accepts water-adjacent doors as mother candidates (filter at line 2038) |
| activation → first bank lag | `PICK(1) + PLANT(1) + 5*cadence(=10) + HARVEST(1) + DROP(1) = 14` after arrival (growth 0→4 is 4 cooldown expiries, first fruit is the 5th; see `predict_tree`'s growth loop 711–731 for the exact referee arithmetic the bot already reproduces). Forced-action sequence: lines 2471–2507 (MOVE/PICK/PLANT then MOVE/DROP/HARVEST/WAIT camp loop) | audit measured median 13 and modeled "travel + 11"; the ±1–3 turn discrepancy is the referee-side initial cooldown of a freshly planted tree, which this source never needs to model. Worth ≤ 2 apples; see Risks |
| steady banked rate | 1 apple / `max(cadence, 2)` = 1 apple / 2 turns. Fruit appears every `cadence`=2 turns (`predict_tree` fruit branch 726–729, fruits cap 3 so nothing is lost), and the camped starter alternates HARVEST/DROP (2-turn bank loop, lines 2477–2483; the mother is a door, so DROP banks) | matches audit "steady bank interval 2 turns", median 121 banked apples |
| fruit → points | 1 point per apple | `rules::score`, lines 179–185 |
| **expected harvests** | `f(turns_left) = max(0, turns_left - travel - 14) / 2` | derived from the above |

Note on `OrchardCycle { first_chop_eta, cycle_eta }` (lines 1937–1941): this struct, `route_cycle` (2076–2105) and
`bankable_cycle` (2106–2163) model **chop** cycles (travel + chop + return + 1 bank turn) — they are the machinery
for `loses_contested_tree`, not for the mother's harvest cadence. They are exactly the right tool for the
**displaced-task** side, not the orchard side. `route_cycle` already enforces `cycle_eta <= turns_left` (line 2101)
and `cycle_eta = first_chop_eta + chop_turns + return_eta + 1 >= 2` since `chop_outcome` returns `turns >= 1` (loop at 756).

### Displaced-task side

**Is the inner policy's chosen starter action/score recoverable?** Partially:

- The wrapper calls `self.inner.commands(view)` **before** the decision (line 2427). The returned `Vec<String>` is in
  scope, and `Self::unit_action_slot(&commands, &unit_ids, starter_id)` (lines 2292–2304) recovers the starter's chosen
  **command string** (MOVE/CHOP/WAIT/PICK...). That gives the task *class* (what the audit instrumented: MOVE 50, CHOP 1, WAIT 3
  of 54 activations) but **no value**.
- The candidate **scores are not recoverable**: `Candidate { command, score: f64, target }` (lines 452–457) lives in a local
  `by_id: BTreeMap<i32, Vec<Candidate>>` built inside `YamoBot::commands` (lines ~1860–1913) and consumed by
  `MoisanBot::select` (873–909); only strings escape. Exposing them would require changing `YamoBot`'s interface/state.
- Even if exposed, inner scores are **heuristic priority units, not points**: CHOP-now is pinned to 10_000 (line 1704),
  banking is 8_000/7_000−eta (534–539), chop targets are `1000*wood/turns` plus a 900/(1+d) denial bonus (823–826),
  conversions are `750/(t+3)` (1719). They order candidates; they do not measure score. So a raw comparison against
  orchard points would be meaningless — a mechanics-level proxy is *required*, not merely convenient.

**Cheap proxy (chosen):** recompute the starter's best repeatable wood-chop bank cycle with functions that already exist
and are `&GameState`-pure:

| Quantity | Source |
|---|---:|
| per-tree first-chop ETA | `bfs_distances` (220) + `ceil_div` (514) |
| tree state on arrival (incl. enemy chop pressure and regrowth) | `MoisanBot::predict_tree` (701–737) |
| chop duration and wood yielded | `MoisanBot::chop_outcome` (738–771) → `(chop_turns, final_size)`; wood = `final_size.min(starter.free_capacity())` |
| return-to-door ETA + 1 bank turn | `bfs_distances` to `geometry.doors`, mirroring `route_cycle` (2097–2100) |
| wood → points | `rules::WOOD_POINTS = 4` (line 139), applied in `rules::score` (184) |

This is exactly the arithmetic the inner policy's own chop scoring uses (`chop_candidates`, 772–839: same
predict → chop_outcome → travel+chop+return+1 pipeline), so the proxy tracks what the inner controller actually wanted
in 51/54 audited activations (MOVE-to-chop / CHOP).

---

## B. Gate formula

Both sides in **game score points by endgame** (rules::score: fruit = 1/unit, wood = 4/unit).

```
turns_left           = 300 - view.turn + 1                          (>= 201 at any Dormant decision, since turn <= 100)
C                    = effective_cooldown(Apple, near_water=true)   = 9 - 7 = 2
travel               = ceil_div(bfs(starter -> mother), move_speed)
first_bank_eta       = travel + 2 + 5*C + 2                          = travel + 14
projected_orchard    = max(0, turns_left - first_bank_eta) / max(C,2)          [apples = points]

per candidate tree t (health > 0, reachable):
  eta_t              = ceil_div(bfs(starter -> t), move_speed)
  (chop_t, size_t)   = chop_outcome(predict_tree(t, eta_t))
  wood_t             = min(size_t, starter.free_capacity())
  cycle_t            = eta_t + chop_t + ceil_div(bfs(t -> nearest door), move_speed) + 1   [>= 2]
  value_t            = 4 * wood_t * (turns_left / cycle_t)                     [integer division]
projected_displaced  = max over t of value_t   (0 if no armed/able starter or no viable tree)

GATE:  projected_orchard - projected_displaced  >=  GATE_MARGIN        (saturating_sub)
```

Worked example with in-code constants (turn 40, travel 2, best tree: 12 cells away at speed 2 → eta 6,
chop 4 turns for 4 wood with capacity ≥ 4, 10 cells back → 5, cycle = 6+4+5+1 = 16):

```
turns_left          = 261
projected_orchard   = (261 - 16) / 2            = 122 points
projected_displaced = 4 * 4 * (261 / 16 = 16)   = 256 points
gate passes iff 122 - 256 = -134 >= GATE_MARGIN     → M must be <= -134 to activate here
```

The displaced side deliberately **overestimates** (it assumes the single best cycle repeats forever; real trees are
consumed and the second worker can absorb the task). Consequently useful `GATE_MARGIN` values are expected to be
**negative**; M is the single tuning knob and must be swept on fresh common seeds per the audit
("mechanics-derived threshold frozen before terminal outcomes are opened").

**Double-counting analysis:**

- The two sides are **mutually exclusive uses of the same worker** for the rest of the game — that is precisely
  opportunity cost; there is no overlap by construction. Orchard apples banked by the starter appear only on the
  orchard side; the displaced side values only the counterfactual chop stream.
- The second worker's output is identical in both branches and appears on neither side — correct.
- Known bias, not double-count: if the second worker takes over the starter's displaced task, the *true* opportunity
  cost is lower than `projected_displaced` (gate too strict → absorbed by negative M). Related: `loses_contested_tree`
  (2199–2252) already vetoes activations where a contested tree would be *lost to the enemy* — that denial component is
  a boolean veto and is intentionally **not** re-counted in points here, so there is no overlap with the existing gate.
- The starter's own carried stock is zero at checkpoint, so neither side can double-count carried goods.

---

## C. Patch plan (exact anchors on the minified one-line file)

### Edit 1 — activation condition

- **Anchor** (occurrences in file: **1**, verified with `grep -o -F | wc -l` and a Python `str.count` assert):

```
if checkpoint&&has_second&&self.can_activate(view,starter,&geometry){
```

- **Replacement:**

```
if checkpoint&&has_second&&self.can_activate(view,starter,&geometry)&&Self::orchard_gate(view,starter,&geometry){
```

The gate is appended **after** `can_activate` in the `&&` chain, so it executes only on states that already pass every
current check (short-circuit), and mother-reachability is already established when it runs.

### Edit 2 — new members of `impl SecureOrchardBot`

- **Anchor** (occurrences: **1**):

```
fn can_activate(&self,view:&GameState,starter:&Unit,geometry:&OrchardGeometry)->bool{
```

- **Replacement:** the new code **prepended** to the anchor (anchor text retained verbatim after it). New code, one line,
  matching file style (`10_000` literal style, `.max(0)`, let-else `else{continue;};` — all already present in the file):

```
const GATE_MARGIN:i32=i32::MIN;fn displaced_projection(view:&GameState,starter:&Unit,doors:&[Cell],turns_left:i32)->i32{if starter.stats.chop_power<=0||starter.free_capacity()<=0||doors.is_empty()||turns_left<=0{return 0;}let from_unit=bfs_distances(&view.walkable,&[starter.cell]);let to_doors=bfs_distances(&view.walkable,doors);let mut best=0;for plant in &view.plants{if plant.health<=0{continue;}let Some(distance)=from_unit.get(&plant.cell)else{continue;};let first_chop_eta=MoisanBot::ceil_div(*distance,starter.stats.movement_speed);let Some(predicted)=MoisanBot::predict_tree(view,plant,first_chop_eta)else{continue;};if predicted.size<=0||predicted.health<=0{continue;}let Some((chop_turns,final_size))=MoisanBot::chop_outcome(view,plant,predicted,starter.stats.chop_power)else{continue;};let wood=final_size.min(starter.free_capacity());if wood<=0{continue;}let Some(return_cells)=to_doors.get(&plant.cell)else{continue;};let cycle_eta=(first_chop_eta+chop_turns+MoisanBot::ceil_div(*return_cells,starter.stats.movement_speed)+1).max(1);best=best.max(crate::game::rules::WOOD_POINTS*wood*(turns_left/cycle_eta));}best}fn orchard_gate(view:&GameState,starter:&Unit,geometry:&OrchardGeometry)->bool{let turns_left=TOTAL_TURNS-view.turn+1;let cadence=effective_cooldown(PlantKind::Apple,true).max(1);let bank_interval=cadence.max(2);let travel=bfs_distances(&view.walkable,&[starter.cell]).get(&geometry.mother).map(|distance|MoisanBot::ceil_div(*distance,starter.stats.movement_speed)).unwrap_or(10_000);let first_bank_eta=travel+2+5*cadence+2;let orchard=(turns_left-first_bank_eta).max(0)/bank_interval;let displaced=Self::displaced_projection(view,starter,&geometry.doors,turns_left);orchard.saturating_sub(displaced)>=Self::GATE_MARGIN}
```

Name-scope facts verified in the minified file: the `moisan` module already imports
`effective_cooldown`, `TOTAL_TURNS` (`use crate::game::rules::{effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,};`)
and `bfs_distances` (`use crate::game::nav::{bfs_distances,is_adjacent,manhattan,next_cell,ortho_neighbors};`);
`WOOD_POINTS` is *not* imported, hence the fully qualified `crate::game::rules::WOOD_POINTS` (the file already uses
`crate::game::rules::` qualification in 4 places). `PlantKind`, `Cell`, `Unit`, `GameState`, `MoisanBot`,
`OrchardGeometry` are all in scope at the insertion point.

### Verification counts (all measured on the actual 55,799-byte file)

| String | Count |
|---|---:|
| `if checkpoint&&has_second&&self.can_activate(view,starter,&geometry){` | 1 |
| `fn can_activate(&self,view:&GameState,starter:&Unit,geometry:&OrchardGeometry)->bool{` | 1 |
| `orchard_gate` (pre-patch) | 0 |
| `displaced_projection` (pre-patch) | 0 |
| `GATE_MARGIN` (pre-patch) | 0 |
| `first_bank` / `cadence` / `bank_interval` (pre-patch, collision check) | 0 / 0 / 0 |

Post-patch compile: `rustc --edition 2021 -O` on the patched one-line file → **success, 0 errors, no new warnings**
(patched copy kept at `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/h1/build/r36-gated.rs`,
57,592 bytes; binaries `base.bin`/`gated.bin` built alongside).

### C0-bridge property

With `GATE_MARGIN = i32::MIN` the gate **always passes**, making behavior byte-identical to current C0:

- The comparison is `orchard.saturating_sub(displaced) >= Self::GATE_MARGIN`. `saturating_sub` never panics and always
  yields a valid `i32`, and every `i32` satisfies `x >= i32::MIN`. (In fact the LHS is bounded: `orchard ∈ [0, 150]`
  since `orchard <= turns_left/2 <= 150`, and `displaced ∈ [0, ~6·10^8]` worst-case — see overflow note — so saturation
  is never even reached.)
- **No overflow:** `turns_left <= 300`; `first_bank_eta <= 10_000 + 14`; `4 * wood * (turns_left/cycle_eta)` with
  `cycle_eta >= 2` (chop_turns ≥ 1, +1 bank) gives at most `4 * wood * 150`; even an absurd `carry_capacity = 10^6`
  stays under `i32::MAX`. All divisors are forced positive: `cadence.max(1)`, `bank_interval = cadence.max(2)`,
  `cycle_eta ... .max(1)`, and `ceil_div` itself returns 10_000 for non-positive divisors.
- **No panics on degenerate states:** every map lookup is `get` + let-else/`unwrap_or`; empty `view.plants` or
  unreachable trees ⇒ `displaced = 0`; chopless/full starter ⇒ early `return 0`; `predict_tree`/`chop_outcome`
  option-returns are `continue`d; their internal loops are bounded at 100 iterations.
- **No side effects:** both new functions are associated fns taking only `&GameState`/`&Unit`/`&[Cell]`/`&OrchardGeometry`;
  no `self` access at all, so no state can drift even on turns where the gate is evaluated and fails.
- The gate sits last in the `&&` chain of the *only* activation site, so all other phases (CarryingSeed/Active/Abandoned
  handling, protect_mother, conflict resolution) are untouched textually and behaviorally.

With `GATE_MARGIN = i32::MAX` the gate **never passes**: LHS ≤ 150 − 0 = 150 < `i32::MAX` (saturating_sub can only
return `i32::MAX` if the true difference exceeds it, impossible with `orchard <= 150`, `displaced >= 0`). This exactly
reproduces the activation-disabled reference: phase stays Dormant, the `view.turn > 100` guard flips it to Abandoned,
and the wrapper passes inner commands through unchanged (Dormant/Abandoned set no `external_idle_unit`/`external_protected_tree`).

---

## D. Risks

1. **Proxy mismatch vs the inner's actual intent.** The candidate scores are locals of `YamoBot::commands` and are in
   heuristic units anyway; the gate re-derives value from mechanics. If the inner starter task was a conversion PICK or
   an iron trip rather than a chop, `displaced_projection` misprices it (audit: 50 MOVE + 1 CHOP + 3 WAIT of 54, so
   chop/travel dominates, but the 3 WAIT cases get `displaced = 0` only if no viable chop exists — a WAITing starter
   with a nearby tree is still scored as if it would chop, overestimating the loss). Direction of error is conservative
   (fewer activations).
2. **Repetition overestimate on the displaced side.** `turns_left / cycle_eta` assumes the best tree respawns; real
   trees are consumed. With M = 0 this can suppress nearly all activations — and the audit shows near-total suppression
   is equivalent to orchard deletion, which *lost* live rating. Mitigations: sweep negative M; or refine to cap cycles
   by the count of viable trees (`(turns_left/cycle_eta).min(viable_tree_count)`) at +~40 bytes. This is the main
   tuning risk, flagged explicitly for the C1 experiment design.
3. **First-bank constant uncertainty.** `travel + 14` is derived from `effective_cooldown` arithmetic, but the initial
   cooldown of a freshly planted tree is referee-side and never modeled in this source; the audit's empirical median is
   13 ("travel + 11" model). Error ≤ ~3 turns ≈ 1–2 apples — negligible relative to M's granularity, but the constant
   should be re-checked against a referee trace before freezing M.
4. **Overflow/panics:** analyzed in C0-bridge section — all divisors forced ≥ 1, all lookups optioned, arithmetic
   bounded far below `i32::MAX`; `saturating_sub` guards the single subtraction that involves the tunable M. Keep the
   comparison as `>=`; switching to `>` breaks the `i32::MIN` bridge argument.
5. **Behavior outside activation:** none. Both anchors are unique (verified counts above); the gate is
   short-circuit-last inside the Dormant branch only; the new fns are pure. The only nonlocal effect is CPU: two extra
   BFS passes plus a per-plant predict/chop scan, executed only on checkpoint turns that already pass `can_activate` up
   to `loses_contested_tree` — which itself already runs the strictly more expensive `bankable_cycle` per plant per
   unit, so the added cost is a fraction of an already-paid budget.
6. **Borrow checker:** non-issue, verified by compilation. At the call site `geometry` is an owned clone, `starter`
   borrows `view` (not `self`), and `Self::orchard_gate` takes no `self` at all, so it composes freely inside the
   `&mut self` `commands` flow and inside the `&&` chain with the `&self`-borrowing `can_activate`.
7. **Target-file provenance.** The task's stated path does not exist; the patch was designed and verified against the
   git blob whose size matches the task byte-for-byte (55,799). If a different r36 variant is the real deployment
   candidate, re-run the two anchor counts (expected 1/1) and the three collision counts (expected 0) before applying —
   the anchors are long enough that silent mis-targeting is effectively impossible.
8. **Default margin.** The patch ships `GATE_MARGIN = i32::MIN` (byte-identical C0 behavior) so it can be merged
   without behavioral risk; the C1 experiment arm is produced by editing that one constant. Freeze the chosen M from
   mechanics reasoning on fresh seeds — do not fit it on the 1,280 audited games.
