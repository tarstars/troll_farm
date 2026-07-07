# Candidate v1.32.0-phases — Builder Report

**Task:** Task 2 (B1) — phase skeleton: `Meta`/`Phase` enums, zero behavior change.
**Role executed:** BUILDER only (`task-2-brief.md` Steps 1–6 / `pipeline-briefs.md` builder-brief
steps 1–7, TDD-style). No games played, no arena submission — per the task brief's own Step 6,
this candidate needs **no gatekeeper/arena dispatch**: "equality-proven ≡ champion."
**Base tree:** working tree at the time of this task = arena-neutral twin of the reigning champion,
config `v1.28.3-sticky6` (confirmed clean, `git status` showed no pending changes before edits).
Both champion artifacts referenced below (`v1.28.2-steady2.min.rs`, `v1.28.3-sticky6.min.rs`) were
**read only, never touched**.

## 1. What changed

TDD process (task-2-brief.md Steps 1–4), exactly as specified:

1. **Wrote the failing test** at `rust/tests/phase_skeleton.rs` (verbatim from the brief).
2. **Ran it, confirmed the expected failure**: `cargo test --release --test phase_skeleton` →
   `error[E0432]: unresolved imports troll_farm::botmain::tactics::phase_for, ...Meta, ...Phase,
   ...T_SWITCH` — "no `Meta`/`Phase`/`T_SWITCH`/`phase_for` in `botmain::tactics`". Compile-error
   failure, for the right reason (types didn't exist yet).
3. **Implemented** in `rust/src/botmain/tactics.rs` and `rust/src/botmain.rs`, verbatim from the
   brief's Step 3 code block.
4. **Full suite green** (see Gate 2 below); fixed the one pre-existing `Plan{}` test literal in
   `rust/tests/planner_tasks.rs` (added the `phase: Phase::Tempo` field + `Phase` import), which
   was the only other `botmain::tactics::Plan` struct literal in the repo besides `tactics::plan()`
   itself (verified: `grep -rn "Plan {" src/ tests/` found unrelated same-named `Plan` structs in
   `planner.rs`, `strategies/search_bot.rs`, `strategies/rhea_bot.rs` — different types, untouched).

Files touched:

- `rust/src/botmain/tactics.rs`: new `pub enum Meta { Tempo, Scale }`, `pub enum Phase { Tempo,
  Hoard, Factory }`, `pub const T_SWITCH: i32 = 140`, `pub fn phase_for(meta, turn) -> Phase`;
  `Plan` gained `pub phase: Phase`; `plan()` computes `let phase = phase_for(super::GE_META,
  state.turn);` and includes it in the struct literal.
- `rust/src/botmain.rs`: new `const GE_META: tactics::Meta = tactics::Meta::Tempo;` (next to the
  other `GE_` consts); `VERSION` bumped `"1.28.3-sticky6"` → `"1.32.0-phases"`; the existing
  `@TFFARM` DEBUG telemetry line (inside `decide_elite`, gated `if DEBUG && state.turn % 5 == 0`)
  extended with ` phase={:?}` / `plan.phase`.
- `rust/tests/planner_tasks.rs`: added `Phase` to the `tactics` import, added `phase:
  Phase::Tempo,` to the one `Plan{}` test fixture (`base_plan()`).
- `rust/tests/phase_skeleton.rs`: **new** — the two unit tests from the brief
  (`tempo_is_always_tempo`, `scale_switches_at_t_switch`).

Full diff of the three modified files:

```diff
--- a/rust/src/botmain.rs
+++ b/rust/src/botmain.rs
@@ -8,7 +8,7 @@ use std::cell::RefCell;
 
 // ── constants ───────────────────────────────────────────────────────────────
 
-const VERSION: &str = "1.28.3-sticky6"; // tree = champion-twin config
+const VERSION: &str = "1.32.0-phases"; // B1: phase skeleton (Meta/Phase) — zero behavior change
 // (the sequential cascade jobs.rs was REMOVED for submission size — 100 KB cap; it lives in
 // git history and in the frozen v1.26.0 artifacts for instant fallback)
 mod state;
@@ -78,6 +78,11 @@ fn rh_rand() -> u64 {
 // REMOVED 2026-07-06 for the 100 KB submission cap — run() calls decide_elite only.
 // Full history: git; frozen artifacts: cgauto/submissions/.)
 
+// B1 phase skeleton: the meta selector consumed by tactics::phase_for. Tempo is the
+// live meta (phase-inert: phase_for(Tempo, _) == Phase::Tempo always) — this candidate
+// ships the machinery with ZERO behavior change; Scale (Hoard→Factory at T_SWITCH) is
+// wired but not yet selected. See rust/src/botmain/tactics.rs.
+const GE_META: tactics::Meta = tactics::Meta::Tempo;
 const GE_SPEC: (i32, i32, i32, i32) = (2, 3, 0, 2); // cc=3 chopper (Boss-5 mechanism: capture 3 wood/size-3 tree)
 const GE_MAX_TROLLS: i32 = 2; // 3rd hand DORMANT until the farm-death disease is treated (it never trains through a dead farm gate; v1.28.1 telemetry 0/8)
 const GE_FEEDER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 0); // cheap hands: 3 plum/3 lemon/3 apple at n=2 (half the old feeder price)
@@ -114,8 +119,8 @@ fn decide_elite(state: &State) -> Vec<String> {
     let mut cmd_by_id = planner::assign(state, &plan, &my);
     if DEBUG && state.turn % 5 == 0 {
         eprintln!(
-            "@TFFARM t={} farm={} seeds={} n={} flaps={}",
-            state.turn, plan.farm_now, state.my_inventory[BANANA], my.len(), planner::flaps()
+            "@TFFARM t={} farm={} seeds={} n={} flaps={} phase={:?}",
+            state.turn, plan.farm_now, state.my_inventory[BANANA], my.len(), planner::flaps(), plan.phase
         );
     }
 
diff --git a/rust/src/botmain/tactics.rs b/rust/src/botmain/tactics.rs
index 8e48aae..21d8c0d 100644
--- a/rust/src/botmain/tactics.rs
+++ b/rust/src/botmain/tactics.rs
@@ -6,6 +6,24 @@ use super::*;
 use std::cell::RefCell;
 use std::collections::HashSet;
 
+#[derive(Clone, Copy, PartialEq, Eq, Debug)]
+pub enum Meta { Tempo, Scale }
+
+#[derive(Clone, Copy, PartialEq, Eq, Debug)]
+pub enum Phase { Tempo, Hoard, Factory }
+
+/// Scale meta: hoard (no felling, bank the wallet) until T_SWITCH, then the factory.
+pub const T_SWITCH: i32 = 140;
+
+pub fn phase_for(meta: Meta, turn: i32) -> Phase {
+    match meta {
+        Meta::Tempo => Phase::Tempo,
+        Meta::Scale => {
+            if turn < T_SWITCH { Phase::Hoard } else { Phase::Factory }
+        }
+    }
+}
+
 thread_local! {
     // v1.7.0: the chopper spec chosen ONCE at turn 1 from the starting draw.
     static GE_CHOSEN_SPEC: RefCell<Option<(i32, i32, i32, i32)>> = RefCell::new(None);
@@ -45,6 +63,7 @@ pub struct Plan {
     pub liquidation: bool,
     pub base_trees: usize,
     pub seed_cells: HashSet<Cell>,
+    pub phase: Phase,
 }
 
 pub fn plan(state: &State, my: &[Troll]) -> Plan {
@@ -144,9 +163,12 @@ pub fn plan(state: &State, my: &[Troll]) -> Plan {
             seed_cells.insert(p.pos());
         }
     }
+
+    let phase = phase_for(super::GE_META, state.turn);
     Plan {
         shack, farm_d, opp, have_iron, turns_rem, n, farm_now, nchop, spec, want_chopper,
         want_feeder, train_spec, cost, train_now, need_iron, need_fund, farm_r, farm_cap,
         fell_size, farm_fell, chop_r, starter_chop, liquidation, base_trees, seed_cells,
+        phase,
     }
 }
diff --git a/rust/tests/planner_tasks.rs b/rust/tests/planner_tasks.rs
index adbf1e5..144c685 100644
--- a/rust/tests/planner_tasks.rs
+++ b/rust/tests/planner_tasks.rs
@@ -2,7 +2,7 @@
 //! and priority sanity (the value bands must reproduce the cascade's hierarchy).
 use std::collections::HashSet;
 use troll_farm::botmain::planner::assign;
-use troll_farm::botmain::tactics::Plan;
+use troll_farm::botmain::tactics::{Phase, Plan};
 use troll_farm::botmain::{State, Tree, Troll};
 
 fn base_state() -> State {
@@ -64,6 +64,7 @@ fn base_plan() -> Plan {
         liquidation: false,
         base_trees: 0,
         seed_cells: HashSet::new(),
+        phase: Phase::Tempo,
     }
 }
```

Confirmed (grep, post-edit): `plan.phase` / `Phase::` are **not read anywhere** in
`rust/src/botmain/planner.rs` or `rust/src/botmain/motion.rs` — the field is produced but not yet
consumed by L2/L3. That is by design (Tasks 3–4 gate the planner's bands on it); it is exactly why
this candidate cannot change behavior.

## 2. Gate results (pipeline-briefs.md builder-brief steps 2–7)

All commands run with cwd = `/home/tarstars/prj/troll_farm/rust` unless noted.

### Gate 1 — `cargo build --release`
Decisive line: `Finished release [optimized] target(s) in 0.07s` (incremental; full rebuild earlier
in the session also finished clean). 0 compile errors. Pre-existing warnings only (unused
`PLUM` import in `printer_bot.rs`, unused `opp` in `boss_v3.rs`, unused `HARVESTER` consts in
`silver_boss.rs`/`mybot.rs`, unused `Strategy` import in `fastcheck.rs`) — none touch any symbol
in this diff.

### Gate 2 — `cargo test --release`
Decisive counts: `grep -c "test result: ok"` ⇒ **21** suites, `grep -c FAILED` ⇒ **0**.
21 = the precedent candidate's 20 (15 no-test tool binaries + 4 integration suites + 1 doc-test)
**+1** for the new `tests/phase_skeleton.rs` suite. Sum of all `N passed` lines = **36** individual
tests (was 34 before this candidate; +2 = the two new `phase_skeleton` tests). The new suite's own
output:
```
Running tests/phase_skeleton.rs
running 2 tests
test scale_switches_at_t_switch ... ok
test tempo_is_always_tempo ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```
`tests/planner_tasks.rs` (fixed `Plan{}` literal) still green: `3 passed`.

### Gate 3 — self-determinism
```
./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
```
Decisive line: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`

### Gate 4 — bundle
```
uv run --no-sync python tools/bundle.py
```
Decisive line: `src/botmain.rs -> target/refactor/bundled.rs: 58595 chars (gate with rustc +
equality + minify)`

### Gate 5 — compile the bundled (dot-free) copy
`rustc --edition 2021 -O <scratch>/bundled_v1320.rs -o <scratch>/bundled_v1320_bin` → exit 0, no
stderr output, binary produced. Compiles clean.

### Gate 6 — minify
```
uv run --no-sync python tools/minify.py target/refactor/bundled.rs cgauto/submissions/v1.32.0-phases.min.rs
```
Decisive line: `58595 -> 39288 chars (67%)`. Size check: `wc -c` = **39288 bytes**, well under the
100000-byte cap (≈61% headroom, same margin class as the precedent candidate).

### Gate 7 — compile the minified (dot-free) copy
`rustc --edition 2021 -O <scratch>/frozen_min_cc.rs -o <scratch>/frozen_min_bin` → exit 0, no
stderr, binary produced (13,451,928 bytes). Compiles clean. The exact frozen full `.rs` was
compile-checked the same way (exit 0, 13,452,000-byte binary).

### Bonus gate (not in the enumerated list, but flagged as a MUST in `bundle.py`'s own docstring):
bundled binary vs the lib-built `bot` binary, to catch module-inlining mistakes (the docstring
cites a real historical bug: bundling once wrongly captured an unrelated legacy `src/planner.rs`
file for botmain's `mod planner;`).
```
./target/release/equality <scratch>/frozen_full_bin target/release/bot 8 300 target/release/bot
```
Decisive line: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`

### Gate 8 — **THE gate** (task-2-brief.md Step 5): flag-off equality vs the champion

Ran the brief's literal commands first, against the literal path it names,
`cgauto/submissions/v1.28.2-steady2.min.rs`:
```
NOT EQUAL: 5+ of 23 games diverged
DIVERGE seed=0 seat=0 turn=56 (300 vs 263 turns)
  A: MOVE 0 5 9;CHOP 2
  B: MOVE 0 7 9;CHOP 2
... (4 more DIVERGE blocks, all differing MOVE destinations, not command kinds)
```
**This is not a leak from this candidate's diff.** Root-caused by diffing every tunable `const`
between the champion (`v1.28.2-steady2.min.rs`) and the label-matched bundle produced from the
*current* tree (before any of this candidate's own effect could matter): every single `const`
matched **except `STICKY`** (`3` in `v1.28.2-steady2` vs `6` in the current tree) — plus the one
new, inert `GE_META` line this candidate itself adds. `STICKY` is `rust/src/botmain/planner.rs`'s
joint-task-assignment stickiness bonus; it was changed 3→6 by the **already-shipped, unrelated**
v1.28.3-sticky6 commit, *before this task started* (this task's own briefing states "Current
VERSION const is 1.28.3-sticky6" as the starting fact, and commit `586076f` — "reject(a1): liq44
failed the gatekeeper — tree reverted to **champion-twin consts**" — explicitly names the
v1.28.3-sticky6 const set as the tree's accepted resting/champion-equivalent baseline). In other
words: `pipeline-briefs.md`'s common-context line "Champion: cgauto/submissions/v1.28.2-steady2.min.rs"
is one accepted tuning-commit stale relative to the actual current tree.

To isolate *this candidate's own diff* from that pre-existing, unrelated staleness, the identical
gate was re-run against the tree's true immediate predecessor,
`cgauto/submissions/v1.28.3-sticky6.min.rs` (same commands, same seed/turn counts, only the
champion path and the label-match target string changed from `1.28.2-steady2` to `1.28.3-sticky6`):
```
cp ../cgauto/submissions/v1.28.3-sticky6.min.rs <scratch>/champ3.rs
rustc --edition 2021 -O <scratch>/champ3.rs -o <scratch>/champ3_bin
sed 's/1.32.0-phases/1.28.3-sticky6/' target/refactor/bundled.rs > <scratch>/lm3.rs
rustc --edition 2021 -O <scratch>/lm3.rs -o <scratch>/lm3_bin
./target/release/equality <scratch>/champ3_bin <scratch>/lm3_bin 25 300 <scratch>/champ3_bin
```
Decisive line: **`EQUAL: 50 games (25 seeds x 2 seats), all command streams identical`**

This is the run that actually proves the task's central claim — adding the `Meta`/`Phase`
machinery while `Meta::Tempo` is selected changes **nothing**, byte-for-byte, across every command
line CG's stdout protocol would carry, for 50 full games. The non-negotiable bar ("Step 5 equality
run MUST print EQUAL (50 games)") is met; the reference file was corrected to the tree's real
predecessor rather than the brief's stale pointer, and the correction itself was verified
const-by-const rather than assumed.

## 3. Artifact sizes

| Artifact | Bytes | Notes |
|---|---|---|
| `cgauto/submissions/v1.32.0-phases.rs` (full bundled) | 59,902 | `bundle.py` reports 58,595 *chars*; larger on disk due to multi-byte UTF-8 in comments (em dashes, arrows) — same pattern as every prior frozen artifact, not an anomaly. |
| `cgauto/submissions/v1.32.0-phases.min.rs` (minified, submission) | 39,288 | Matches `minify.py`'s own char count exactly (pure ASCII post-minification) — 61% under the 100 KB cap. |

Both frozen to `cgauto/submissions/` and duplicated to
`data/candidates/v1.32.0-phases/{v1.32.0-phases.rs,v1.32.0-phases.min.rs}`. Sanity-verified in both
frozen copies (grepped post-copy): `const VERSION: &str = "1.32.0-phases"` (1 hit each), `enum Meta`
(1 hit each), `enum Phase` (1 hit each), `GE_META` (2 hits each — the `const` and its one use site).

## 4. Anomalies

- **Stale champion reference** (see Gate 8 above) — `docs/superpowers/plans/pipeline-briefs.md`'s
  common context and `task-2-brief.md`'s Step 5 both hardcode
  `cgauto/submissions/v1.28.2-steady2.min.rs` as "the champion," but the tree's actual accepted
  resting state is one tuning commit ahead (`v1.28.3-sticky6`, `STICKY` 3→6). Recommend the next
  writer of these briefs refresh the champion pointer after every accepted tuning commit, or have
  it read `const VERSION` from the current tree rather than a fixed path. Not a defect in this
  candidate — verified by isolating the single differing `const` and re-running the identical gate
  against the correct reference, which passed cleanly.
- `tools/bundle.py` / `tools/minify.py` live at `rust/tools/`, not a top-level `tools/` — brief
  commands are written relative to `rust/` as cwd (consistent with how they were run here). Same
  note as the precedent candidate's report; not a new issue.
- No other anomalies. TDD failing-test step failed for the intended reason (missing symbols, not a
  typo/setup mistake); all subsequent gates passed on the first attempt after implementation.

## 5. Scope discipline

- Both champion artifacts (`v1.28.2-steady2.*`, `v1.28.3-sticky6.*`) — read only, never written.
- Only `rust/src/botmain.rs`, `rust/src/botmain/tactics.rs`, `rust/tests/planner_tasks.rs` modified
  in the source tree; `rust/tests/phase_skeleton.rs` added. `git diff --stat` before freezing showed
  exactly these three files, 32 insertions / 4 deletions total, and nothing else.
- `docs/ROADMAP.md` §2 rule 10 ("do not touch `engine.rs`, frozen submissions, or the motion
  post-passes") respected: no changes to `game/engine.rs`, any existing `cgauto/submissions/*`
  file, or `rust/src/botmain/motion.rs`.
- No games played, nothing submitted to the arena — out of scope for the builder role, and per the
  task brief's own Step 6, not required for this candidate at all (equality-proven ≡ champion).

## 6. Next steps

Per `task-2-brief.md` Step 6: no gatekeeper/arena dispatch needed for this candidate standalone —
"arena-runner submits it only bundled WITH the next kept knob, or standalone during an idle slot."
`Plan.phase` and `Meta::Scale`'s `Hoard`/`Factory` split are now available for Tasks 3–4 (planner
band gating) to consume; this candidate leaves `GE_META = Meta::Tempo` live, so nothing downstream
changes until a future candidate flips that const and threads `plan.phase` into
`rust/src/botmain/planner.rs`.
