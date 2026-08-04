# Integration seam report — banana wood-printer on parent a8eb3b2b

Status: PUBLISHED 2026-08-04. Produced by a claude_1 subagent; all five insertion anchors,
all collision counts, replace_action reuse, and the compactor-idempotence claim
(parent == compact(parent) + newline) independently re-verified by claude_1 against the
frozen parent bytes before publication.

Parent verified: `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/banana/parent-a8eb3b2b.min.rs`,
62,725 bytes, sha256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` (recomputed, matches task record).
All substring counts below were measured against this exact file.

## A. Parent map (parent vs readable relative `family-readable-guide.rs`, r36 simplified E7a)

Same skeleton in both: `mod game::{types,rules,nav,protocol}`, `mod bot::moisan` with
`MoisanBot` (worker policy core), `YamoBot` (opening/regeneration layer), `SecureOrchardBot`
(top wrapper), `pub trait Bot`, `fn main()`. The parent is the earlier, config-heavy member;
the relative deleted the config plumbing. Counts are exact substring occurrences (parent / relative).

| Feature / plumbing | In parent? | In relative? | Evidence substring (parent) |
|---|---|---|---|
| `YamoOpeningPolicy` struct + `TUNED_CARRY` const | yes (8 / 2) | no (0) | `pub struct YamoOpeningPolicy{pub train_horizon:i32,` |
| `SecureOrchardBot::with_policy` ctor | yes (2) | no (0) | `Self::with_policy(YamoBot::tuned_carry_regeneration_transit_idle_harv` |
| `opponent_eta_penalty` threading | yes (14) | no (0) | `opponent_eta_penalty:i32,external_idle_unit:Option<i32>,` |
| `protected_tree` threading | yes (19) | yes (19) | `external_protected_tree:Option<Cell>,}` |
| `door_unblocking` switch | yes (4) | no (0) | `bot.door_unblocking=true;` |
| `idle_harvest` switches | yes (11: incl. `idle_harvest_clock_only` x3) | partial (4, name only inside `tuned_carry_...idle_harvest`) | `bot.idle_harvest=true;` |
| `partial_bank_transit` switch | yes (4) | no (0) | `bot.partial_bank_transit=true;` |
| `persistent_regeneration` switch | yes (10) | no (0) | `bot.persistent_regeneration=true;` |
| `regeneration_commitments` map | yes (9) | yes (8) | `regeneration_commitments:BTreeMap<i32,PlantKind>,` |
| `external_idle_unit` / `external_protected_tree` reservation hooks in YamoBot | yes (4 each) | yes (4) | `if let Some(id)=self.external_idle_unit{by_id.insert(id,vec![MoisanBot::wait()]);}` |
| SecureOrchardBot policy fields (`minimum_enemy_eta` x4, `require_idle_starter` x4, `minimum_enemy_door_distance` x4, `minimum_worker_speed` x5) | yes | no (relative struct has only 7 fields, no policy knobs) | `plant_attempted:bool,minimum_enemy_eta:i32,require_idle_starter:bool,` |
| `OrchardPhase{Dormant,CarryingSeed,Active,Abandoned}` (21) | yes, same 4 phases | yes (21) | `enum OrchardPhase{Dormant,CarryingSeed,Active,Abandoned,}` |
| `PlantKind::Banana` (`Banana` x10, all PlantKind sites) | yes | yes (10) | `enum PlantKind{Plum,Lemon,Apple,Banana,}` |
| `banana_` identifiers | **0** | 0 | — |

`main()` (parent): constructs `SecureOrchardBot::new()` and loops
`read_turn -> bot.commands(&view) -> writeln!(out,"{}",commands.join(";"))`.
Parent `SecureOrchardBot::new()` = `Self::with_policy(YamoBot::tuned_carry_regeneration_transit_idle_harvest(),8,false,11,1,)`;
the relative's `new()` builds the struct literal directly. Same phase machine and same
`initialize / reconcile_initial_natural / replace_action` shape; where they differ, parent is truth.

Wrapper post-edit precedent (parent): `SecureOrchardBot` computes a `replacement` action for its
reserved starter and applies it with
`fn replace_action(commands:&mut Vec<String>,unit_ids:&[i32],id:i32,action:String)` (3 occurrences),
and reserves the worker inside YamoBot via `external_idle_unit` (set every turn in
`impl Bot for SecureOrchardBot`: `self.inner.external_idle_unit=reserve_orchard.then_some(self.starter_id).flatten();`).

## B. Seam design

Constraint restated: insert-only transform. The modified source must be
`parent + inserted strings at unique anchors`; inverse transform = delete those exact strings.
No replacements, no delimiter comments (minified). Therefore every behavioral change must be
expressible as pure insertion — the two enabling tricks are (1) Rust let-shadowing in `main`
and (2) a new reservation field in `YamoBot` that defaults to `None`.

### Recommended architecture: outer `BananaBot` wrapper (SecureOrchardBot precedent)

`BananaBot{inner:SecureOrchardBot, phase:BananaPhase, worker:Option<i32>, ...}` placed **inside
`mod moisan`**, implementing `Bot`. Per turn:

1. Update `BananaPhase` (Dormant / Planting / Renewing / Converting / Banking / Abandoned — exact
   lifecycle per task record; claude_1 pins the invariants).
2. Arbitration (the single deterministic point): read `self.inner.starter_id` and
   `self.inner.phase` (module-private fields are visible inside `mod moisan` — legal, no
   accessor insertion needed). The banana worker is chosen deterministically (e.g. lowest-id
   player-0 unit) **always excluding** the orchard starter, and only when a non-starter,
   non-funding worker exists. Apple orchard and banana plot can never claim the same worker.
3. If active: set `self.inner.inner.banana_idle_unit=Some(worker)` **before** delegating
   (YamoBot reads it during the delegated call); else set it to `None`.
4. `let mut commands=self.inner.commands(view);`
5. If active: compute the banana action and apply it via the existing
   `SecureOrchardBot::replace_action(&mut commands,&unit_ids,worker,action)` (same-module private
   assoc fn — reusable, no insertion into SecureOrchardBot needed).
6. Return `commands`.

### Insertion set (5 insertions; every anchor verified count == 1 in the parent)

| # | Anchor (exact parent substring, count=1) | Insert position | Inserted string (sketch) |
|---|---|---|---|
| I1 | `pub struct SecureOrchardBot{` | immediately **before** anchor | entire banana block: `enum BananaPhase{...}pub struct BananaBot{inner:SecureOrchardBot,...}impl BananaBot{pub fn new(inner:SecureOrchardBot)->Self{...}...}impl Bot for BananaBot{fn commands(&mut self,view:&GameState)->Vec<String>{...}}` (item order is irrelevant in Rust; `Bot` is already in scope in moisan) |
| I2 | `external_protected_tree:Option<Cell>,}` | after the `,` inside anchor (before `}`) | `banana_idle_unit:Option<i32>,` |
| I3 | `external_protected_tree:None,}}` | after the first `,` inside anchor | `banana_idle_unit:None,` |
| I4 | `if let Some(id)=self.external_idle_unit{by_id.insert(id,vec![MoisanBot::wait()]);}` | immediately **after** anchor | `if let Some(id)=self.banana_idle_unit{by_id.insert(id,vec![MoisanBot::wait()]);}` |
| I5 | `else{return;};let mut bot=SecureOrchardBot::new();` | after `let mut bot=SecureOrchardBot::new();` | `#[allow(unused_mut)]let mut bot=crate::bot::moisan::BananaBot::new(bot);` (shadowing rebind; fully qualified path avoids a `use` insertion; the outer allow-attr suppresses the `unused_mut` warning the shadowing induces on the *new* binding — see risk R2) |

Verified counts in the parent: each anchor above occurs exactly 1 time; the collision-side
counts `BananaBot` = 0, `BananaPhase` = 0, `banana_idle_unit` = 0, `banana_` = 0,
`#[allow(` = 0. Every inserted string contains a `Banana`/`banana_` token or `#[allow(unused_mut)]`,
none of which occur in the parent, and no inserted string is a substring of another, so the
**inverse transform is well-defined**: delete each inserted string (each occurs exactly once in
the modified file, pairwise non-overlapping) -> parent bytes restored. The patch script must
assert, mechanically: (a) each anchor count == 1 in parent; (b) each inserted string count == 0
in parent and == 1 in output; (c) sha256(output with insertions removed) == `a8eb3b2b...`.

### Alternatives considered

- **Fields+methods inside SecureOrchardBot**: rejected. Requires insertions into the struct
  literal of `new`/`with_policy`, and into the middle of the largest, densest method
  (`impl Bot for SecureOrchardBot::commands`, whose interior anchors are long and fragile);
  entangles two phase machines in one struct; inertness becomes a data-flow argument instead of
  a structural one; ablation (inverse transform) still possible but the seam is smeared across
  the hottest code.
- **Sibling struct with arbitration inside SecureOrchardBot**: rejected. The arbitration point
  would live inside SecureOrchardBot's turn logic (insertions mid-body again), and
  SecureOrchardBot would need to own/poll the sibling — more coupling than the wrapper, same
  risk profile, no benefit.
- **Outer BananaBot wrapper (chosen)**: follows the proven SecureOrchardBot pattern (wrapper +
  pass-through + dedicated reservation field + `replace_action` post-edit); one arbitration
  point at the top of the turn; dormant path is structurally the identity function; smallest
  insertion count at the most stable anchors (struct/impl boundaries and unique one-off
  statements, not expression interiors).

## C. Research -> compact pipeline

Compactor: `/home/tarstars/prj/troll_farm-claude_1/cgauto/compact_rust_source.py`
(lexical; CLI `python3 compact_rust_source.py SOURCE OUTPUT`).

Tested on the parent (copy in scratchpad, parent untouched):

- **Idempotence on the minified parent**: `62725 -> 62724` bytes. The output equals the parent
  **minus the trailing `\n`** (verified byte-wise: `parent == compact(parent) + b"\n"`, first
  difference is only at EOF). So the compactor is idempotent modulo final newline; any equality
  assert must append/normalize the trailing newline.
- **Full round trip `rustfmt(parent) -> compact`**: FAILS byte-exactness. `rustfmt --edition 2021`
  expands the parent to 2,780 lines; recompacting yields 62,748 bytes with **28 diff ops** vs the
  parent: 13 inserted trailing commas (rustfmt adds `,` before `)` in wrapped fn signatures,
  first at byte 4344: parent `...speed:i32)->Cell` vs round-trip `...speed:i32,)->Cell`),
  a `use std::io::{self,Write};` reordering in the main section, 6/5 brace insert/delete
  normalizations, plus the EOF newline. All cosmetic, but check 1 demands byte-exactness, so
  **"readable master -> compact == parent+insertions" is not achievable with rustfmt output as
  the master**.

Concrete build flow that satisfies checks 1 and 2 despite this:

1. **Canonical compact candidate is built by the patch script, not by the compactor**:
   `candidate.min.rs := apply_insertions(parent bytes, [I1..I5])`, with the three mechanical
   asserts from section B. This *is* the "derive compact source mechanically" requirement, and
   the inverse transform is trivially the string deletions.
2. **Banana insertion strings are still authored readable**: each block (I1 especially) is
   written as readable Rust in the research tree, then compacted **per block** with
   `compact_rust_source.py`; since we author these blocks fresh, we keep them in the compactor's
   fixed point style (no wrapped-signature trailing commas), so
   `compact(readable_block) == inserted_string` is asserted per block in CI.
3. **Readable research source of the whole program** is derived mechanically in the reverse
   direction: `research.rs := rustfmt(candidate.min.rs)` — archived alongside the candidate.
   It is independently readable and mechanically reproducible.
4. **Research/compact equality** (check 3) is then proven behaviorally, as the task already
   requires: compile both `research.rs` and `candidate.min.rs`, replay the open panel + all
   supplied banana-live replays, assert identical command streams. (Byte-derivation equality
   between the two full sources is impossible with this rustfmt/compactor pair; behavioral
   equality on the mandated panels is the intended gate.)

Obstacle summary: (a) trailing-newline drop — normalize in the assert; (b) rustfmt trailing-comma
and use-ordering normalization — solved by making parent+insertions canonical and deriving the
readable view from it, plus per-block round-trip asserts for the newly authored code.

## D. Risk list

- **R1 Borrow/order at the arbitration point**: `banana_idle_unit` must be written *before*
  `self.inner.commands(view)` is called (YamoBot reads it inside that call), and must be reset to
  `None` on every dormant turn — `SecureOrchardBot::commands` overwrites `external_idle_unit`
  every turn but will never touch `banana_idle_unit`, so stale reservations are BananaBot's
  responsibility. Accesses are sequential `&mut self`; no aliasing. Do NOT reuse
  `external_idle_unit` (overwritten each turn by the orchard — that is exactly the contention
  the dedicated field avoids).
- **R2 Shadowing warning**: the rebind in I5 makes rustc warn `unused_mut`-adjacent lint noise on
  one of the bindings depending on final shape; the inserted `#[allow(unused_mut)]` covers it.
  Verify with `cargo build --release 2>&1` that the candidate compiles warning-clean (check 8
  wants a clean standalone optimized compile; runtime stderr must be empty regardless).
  If the attribute placement on the let-statement proves awkward, drop it and accept the
  compile-time warning — it never reaches runtime stderr — but decide once and record it.
- **R3 Name collisions**: verified absent from parent: `banana_` (0), `BananaBot` (0),
  `BananaPhase` (0), `banana_idle_unit` (0). `Banana` occurs 10 times, all `PlantKind::Banana` /
  `"BANANA"` protocol sites — the plant kind exists and is what the module targets; choose all
  new identifiers with the `Banana`/`banana_` prefix so every inserted string stays unique.
- **R4 Module-privacy coupling**: BananaBot reads `SecureOrchardBot.starter_id`/`phase` and
  writes `YamoBot.banana_idle_unit` via same-module field visibility, and reuses private
  `SecureOrchardBot::replace_action`. Legal only while I1 lands inside `mod moisan` — the I1
  anchor guarantees that. Any future refactor moving BananaBot out of moisan breaks compile.
- **R5 replace_action fallback**: it `push`es when the unit has no slot; the banana worker is
  always a live player-0 unit present in the inner command set, but the semantic tests
  (check 7, destroyed/occupied recovery) must cover the worker-death turn so a pushed duplicate
  command can never appear.
- **R6 Worker scarcity / funding invariant**: activation gate must require a claimable worker
  that is neither the orchard starter nor the pre-funding second worker ("preserve second-worker
  funding before denial work" + no TRAIN displacement, checks 5/7). With <=1 eligible worker,
  BananaPhase stays Dormant. This is a spec invariant claude_1 must restate explicitly before
  implementation (task record demands the ambiguity be restated as invariants).
- **R7 Compile-time surface**: I1 must only reference items already in scope in moisan
  (`GameState`, `Cell`, `PlantKind`, `BTreeMap/BTreeSet`, `MoisanBot`, `YamoBot`,
  `SecureOrchardBot`, `Bot`, nav helpers). Keep the block self-contained; unused helpers trigger
  dead-code lints — either keep the block minimal or open it with `#[allow(dead_code)]`.
  Byte budget: parent 62,725 + insertions must stay < 100,000 (check 8) — ~37 KB headroom.
- **R8 Check-4 inertness proof obligation**: structural argument — the only behavioral
  insertions are I4 (no-op while `banana_idle_unit == None`) and I5 (identity delegation while
  `BananaPhase == Dormant`); I1–I3 add unreached code and a `None` field. Evidence to supply:
  (a) replay equality parent-binary vs candidate-binary command streams over a broad open panel;
  (b) a deterministic activation detector (separate probe build writing activation turn/state to
  a file — never stderr) proving which games never left Dormant, so the equality claim is scoped
  to genuinely dormant games and every activated game moves to the semantic suite.
  **The existing 25-game packet is NOT sufficient**: it was assembled for the r36 relative's
  lineage (its own annotation: orchard fired in 1 of 25 packet games) and says nothing about
  banana activation on this parent. `local_codex_1` must supply: the broad open panel for the
  dormant-equality claim, every banana-live replay (check 3), and the host-only gate on game
  `897829265` (check 6, period-2 windows turns 20–29 and 269–280).
