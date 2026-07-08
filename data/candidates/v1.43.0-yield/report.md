# Candidate v1.43.0-yield — Builder Report

**Task (design D2, user architecture request 2026-07-08):** "picker stands on the banana
tree, picking fruits, and it blocks the way of the wood gatherer -- solve it at the level
of missions: urgency, blocking." Engine fact (verified in the brief, re-confirmed against
`rust/src/game/engine.rs::apply_moves` :204-280 before touching anything): a same-team
STATIONARY troll (doing CHOP/HARVEST/PLANT/MINE/PICK/DROP at its own cell) is a hard wall
for landings -- `occupied` starts as all of that player's positions and a stationary
unit's cell never leaves it, no exception, not even `resolve_blocking`. That can fully
block a lower-ms mover whose queued task is worth far more than the blocker's. The fix:
`planner::yield_pass` -- after `assign()` + the first `motion::solve_moves`, detect that
exact shape and, iff the blocked mover's assignment strictly outranks its blocker's
(same i64 values `assign()` already computed), let the blocker yield ONE turn (re-match
to its own next-best candidate, re-solve motion once more). Bounded to at most one
(mover, blocker) pair per turn -- no cascade.

## Worktree state (pre-task, resolved)

`git log --oneline -1` showed `fa33b21` ("feat: sim Bronze support + tuned wood economy
(v0.6.1)") -- the pre-Rust-rewrite Python Bronze bot, badly stale. Cross-checked against
`git worktree list`: every OTHER worktree in `.claude/worktrees/` was already advanced to
a Jul 5-8 commit; this one was uniquely still at the Jun 24 point -- i.e. this specific
slot had never been used by a builder before (a different slot,
`agent-ab5cee1391dc2f5d3`, is where `v1.42.0-idlefruit` was actually built, per that
candidate's own report describing the identical fa33b21 starting point -- each worktree
slot independently needs its one-time fast-forward the first time it's assigned). `git
merge-base --is-ancestor fa33b21 session-2026-07-01` confirmed `fa33b21` is a strict
ancestor (zero divergent commits on the worktree's own branch,
`worktree-agent-a5a0b6adf1096dd10`); `git status --porcelain` in the worktree was clean.
Fast-forwarded via `git merge --ff-only session-2026-07-01` (non-destructive by
construction -- a fast-forward only advances a pointer, and there was nothing local to
lose). Landed on `6c661ee` ("gate(idlefruit): PASS -- wood 43.8 (ref 51.2), delta -8.2
(ref -12.3), harvest+drop 375 vs 291 base (+29%)"), exactly the commit the brief's base
line describes ("includes v1.41.0-nopickloop + v1.42.0-idlefruit"). Confirmed
`rust/`/`cgauto/`/`data/candidates/v1.43.0-yield/brief.md` all present post-fast-forward,
and the pre-task test suite baseline: `cargo test --release` -> **58 passed, 7 ignored, 0
failed**, matching the task's stated baseline exactly.

## Design

### Layer seams (read before choosing where the code lives)

Read the actual call site in `botmain.rs::decide_elite` before writing anything:
`tactics::plan` -> `planner::assign` (renders a `HashMap<i32,String>` of commands; the
i64 candidate VALUES it computes internally were, pre-this-candidate, thrown away after
picking a winner) -> build `intents` from any `"MOVE "`-prefixed command -> the FIRST
`motion::solve_moves` -> a landing-rewrite loop (`if cur != Some(cell)`, rewrite the MOVE
target to the actual landing; leave it as-issued otherwise, since "the engine blocks it
harmlessly") -> `motion::watchdog`. The brief calls for `yield_pass` to hook "between
assign and the FINAL solve_moves" -- i.e. right after that first landing-rewrite loop,
before the watchdog.

### The value/matrix problem, and how it's solved without changing `assign()`'s signature

`yield_pass` needs two things `assign()` never exposed: (a) the i64 value of what a
troll was actually assigned, and (b) that troll's own next-best alternative. Changing
`assign()`'s return type to carry this would touch every existing call site (it's
indexed as a plain `HashMap<i32,String>` in `pickloop.rs`/`idlefruit.rs`/`race_check.rs`/
`planner_tasks.rs`/etc.) -- against "keep the diff minimal." Instead (commit `dad1e52`,
pure refactor, no behavior change): extracted the exhaustive joint search itself into a
private `joint_solve(state, plan, my) -> Joint` (a pure function, no thread-local
writes) and the per-`Cand` render match into a private `render_one(...)`. `assign()`
became a thin wrapper: `joint_solve` then render + the existing FLAPS/LAST_TGT
bookkeeping (unchanged). `Joint::value(id)` / `Joint::next_best(id)` (both
bounds-checked via `.get`, never indexing) are the ONLY new surface `yield_pass` needs --
it calls `joint_solve` a SECOND time (cheap: K<=8 candidates/troll, n<=~4 trolls in
practice, no thread-local side effects to double-count) rather than plumbing a shared
result through `botmain.rs`'s call site, which would have meant restructuring
`decide_elite`'s flow instead of adding one `if let` block to it.

Because `yield_pass` needs `Cand`/`Kind` (both private to `planner.rs`) to read
`next_best`'s render, it lives in `planner.rs` itself -- the brief's own "or a small
module" alternative would have needed those types made `pub`, leaking planner-internal
representation into the crate's public surface for no benefit.

### `motion::best_progress` -- the detection primitive

Detection ("would excluding just this ONE teammate's cell let the mover advance?") needs
solver-side knowledge (the same per-troll candidate-landing generation
`motion::solve_moves` already does internally), so it lives in `motion.rs`:
`best_progress(state, t, goal, stationary) -> i32` mirrors `solve_moves`'s per-troll
candidate loop, reduced to just the max progress value (no sorted/truncated list, no
joint search -- the caller controls `stationary` directly, so there's nothing to
coordinate for a single troll). Calling it twice -- once with the full stationary set
(should reproduce the observed "0 progress, blocked" state) and once with one
teammate's cell excluded -- cheaply identifies whether that ONE teammate is the sole
blocker, without a joint re-solve.

### `yield_pass`'s algorithm (planner.rs)

1. **Detect:** derive `moving`/`stationary` from `cmd_by_id` exactly as
   `motion::solve_moves` does (a troll is "moving" iff its rendered command starts with
   `"MOVE "`). For each mover (canonical id order) whose first-solve `landing == its
   current cell` (zero progress), and for each stationary teammate (canonical id
   order): test `motion::best_progress` with that one teammate's cell excluded from the
   stationary set. If it's `> 0`, that teammate is a qualifying blocker.
2. **Policy:** `value(mover) > value(blocker)` (strict, via `Joint::value` -- the exact
   i64s `assign()` already computed). Take the FIRST qualifying pair in this canonical
   order and stop (`break 'outer`) -- deterministic, no scan for a "better" pair.
3. **Act:** `Joint::next_best(blocker)` (the blocker's own next candidate in its already
   sorted, top-K list -- never anyone else's). Render it via the same `render_one` used
   by `assign()`. Replace the blocker's entry in a cloned `cmd_by_id`, rebuild `intents`,
   call `motion::solve_moves` ONCE more, and apply the identical
   "rewrite-only-if-landing-differs" convention to the result.
4. **Bound:** exactly one pair is ever acted on (the `break 'outer` in step 2 plus no
   looping construct anywhere in the function). If the blocker's own re-match is itself
   blocked, the caller simply gets that (unsuccessful) attempt back -- "next turn
   re-detects," per the brief.

Telemetry: a `YIELDS` thread-local (mirrors the existing `FLAPS` pattern) + `pub fn
yields()`, reset in `reset()`; a DEBUG-gated `@TFYIELD t=<turn> blocker=<id> mover=<id>`
line fires when a yield is attempted (`super::DEBUG` is reachable from `planner.rs`
because Rust's default item visibility extends to descendant modules -- confirmed
empirically, not just assumed, since the same pattern was already relied on by
`tactics.rs` reading `botmain`-private `GE_*` constants before this candidate).

**CONTRACT (documented in `yield_pass`'s doc comment):** call at most once per turn,
mirroring `assign()`'s own single-call-per-turn contract for its thread-local
bookkeeping. The one-round bound is enforced by that call discipline (a single call
site in `botmain::decide_elite`), not by internal re-entrancy tracking -- `stationary` is
re-derived from `cmd_by_id` each call, and a troll whose yield attempt FAILED (its
re-match still landed on its own cell) nonetheless shows a `"MOVE "` command. A
hypothetical second call in the same turn would see it as safely non-stationary and
could wrongly consider cascading past it (hand-traced through the exact
`yield_single_round` fixture below -- see the TDD section for the trace).

### `botmain.rs` wiring

```rust
let landing = motion::solve_moves(state, &my, &intents);
for (id, cell) in &landing {
    let cur = my.iter().find(|t| t.id == *id).map(|t| t.pos());
    if cur != Some(*cell) {
        cmd_by_id.insert(*id, format!("MOVE {} {} {}", id, cell.0, cell.1));
    }
}
if let Some((new_cmds, _new_landing)) = planner::yield_pass(state, &plan, &my, &cmd_by_id, &landing) {
    cmd_by_id = new_cmds;
}
motion::watchdog(state, &my, &mut cmd_by_id);
```

(The pre-existing `for (id, cell) in landing` loop was changed to iterate `&landing`
instead of consuming it by value, so `landing` is still available to pass into
`yield_pass` afterward -- the only other change to this function besides the new `if
let` block and the `VERSION` bump.)

## TDD

New file `rust/tests/yield_pass.rs`. All three fixtures share a 1-wide horizontal
corridor (`(1,2)..=(n,2)` walkable, shack at `(0,2)` not walkable) whose sole
shack-adjacent cell is `(1,2)` -- the geometry that makes a mid-corridor stationary troll
a genuine hard block for anyone behind it at `movement_speed=1` (its only in-range
landing candidate IS the blocker's cell).

### Test 1 -- `yield_corridor`

Picker `S` (id 1, pure harvester) stands at `(3,2)` on a ripe PLUM -- band 38
(idle-fruit), value `38*BAND`, renders `"HARVEST 1"` (stationary). Chopper `M` (id 2,
full of wood, `movement_speed=1`) sits at `(4,2)`, directly behind -- band 80 (full ->
bank, target = the sole camp cell `(1,2)`), value `80*BAND`. `M`'s only within-range
landing candidate is `S`'s cell, a hard wall -- `M` is fully blocked (zero progress) even
though `80*BAND` is vastly greater than `38*BAND`.

**RED (verified against commit `dad1e52`'s `None`-returning stub, run BEFORE any real
logic existed):**

```
running 2 tests
test no_yield_when_blocker_outranks ... ok
test yield_corridor ... FAILED

---- yield_corridor stdout ----
thread 'yield_corridor' panicked at tests/yield_pass.rs:152:5:
expected a yield: M's full-bank task (80*BAND) outranks S's idle-fruit task (38*BAND)

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Both "setup check" assertions (M starts fully blocked at `landing == (4,2)`; S starts
stationary-harvesting) passed silently before reaching the real assertion -- confirming
the hand-derived fixture geometry was correct on the first try, and the failure is
exactly the intended one (the stub never yields, so `result.is_some()` fails).

**GREEN (post-fix, commit `7c2d466`):**

```
test yield_corridor ... ok
```

### Test 2 -- `no_yield_when_blocker_outranks` (regression pin, Test-B style)

Same corridor and adjacency, roles/values swapped: `S` now stands on a ripe BANANA at
`(3,2)` -- band 75 ("wanted" fruit), value `75*BAND`. `M` is now a pure starter (no
bank/chop task) chasing an idle-fruit PLUM at `(2,2)`, beyond `S` -- band 38, value
`~38*BAND`. `M` is still fully blocked by `S` (identical detection shape), but now
`value(S) = 75*BAND > value(M)` (approximately `38*BAND`), so the policy's strict `>`
must NOT fire.

Passed against BOTH the `None`-stub (trivially -- a no-op never yields, confirmed in the
same RED run above, first line: `test no_yield_when_blocker_outranks ... ok`) AND the
real implementation (confirmed again after `7c2d466`) -- a true non-regression pin, not a
RED/GREEN pair, exactly mirroring `tests/idlefruit.rs`'s Test B precedent.

### Flip-check (proves the pin is live, not vacuous)

Per the task's D1-style instruction: temporarily inverted the comparison,
`if vm > vs` -> `if vm < vs` (one line, `src/botmain/planner.rs:766` at the time). Reran
both tests:

```
running 2 tests
test yield_corridor ... FAILED
test no_yield_when_blocker_outranks ... FAILED

---- yield_corridor stdout ----
thread 'yield_corridor' panicked at tests/yield_pass.rs:152:5:
expected a yield: M's full-bank task (80*BAND) outranks S's idle-fruit task (38*BAND)

---- no_yield_when_blocker_outranks stdout ----
thread 'no_yield_when_blocker_outranks' panicked at tests/yield_pass.rs:190:5:
S's task (75*BAND) outranks M's (38*BAND-ish): no yield must fire, got Some(({1: "MOVE 1 3 2", 2: "MOVE 2 2 2"}, {2: (4, 2), 1: (3, 2)}))

test result: FAILED. 0 passed; 2 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Both tests fail in exactly the predicted, complementary way: `yield_corridor`'s true
scenario (`80*BAND` vs `38*BAND`) is now rejected (`80*BAND` is not `< 38*BAND`), and
`no_yield_when_blocker_outranks`'s false scenario is now wrongly *accepted*
(`38*BAND`-ish IS `< 75*BAND`) -- visibly: `S`'s rendered command becomes `"MOVE 1 3 2"`,
its own band-52 self-targeting candidate (a BANANA tree generates both a band-75
Harvest-standing AND a band-52 self-MoveTo candidate for the same cell; `next_best` after
suppressing band 75 picked up band 52 here). This is a cleaner, more symmetric flip-check
than a single-test flip: inverting the one comparison breaks both tests in the exact
complementary direction their respective designs predict, proving neither is vacuous.
Reverted (`if vm > vs`), reran -- both green again (confirmed via the full suite run
below, gate 4).

### Test 3 -- `yield_single_round` (the bound)

Corridor `(1,2)..(4,2)`, a dead end. An UNRELATED second stationary troll `S2` (id 3, an
idle chopper doing `ChopHere` on a fruitless banana -- deliberately NOT another
fruit-harvester, so it never generates a competing candidate in `S1`'s own list; a
fruited tree would have, muddying the trace) sits at `(2,2)` -- exactly the cell `S1`'s
own next-best candidate (`Park`'s scarce-camp ring-2 redirect: the shack's only
ortho-neighbor is `(1,2)`, so `camp_cells=1 <= 2`, and the only walkable manhattan-2 ring
cell is `(2,2)`) would want to move to. `S1` (id 1) stands on a ripe PLUM at `(3,2)`,
blocking `M` (id 2, full-bank chopper) exactly as in `yield_corridor`.

Detection correctly finds only `(M, S1)` -- removing `S2` alone (keeping `S1`) does NOT
unblock `M` (`best_progress` stays 0, since `S1`'s cell is still excluded), so `S2` never
qualifies as a candidate blocker in the first place. `(M, S1)` is acted on: `S1` is
re-matched to `Park`, which -- unaware of `S2`'s PHYSICAL occupancy (`park_cmd` only
tracks its own `claimed` bookkeeping, not troll positions) -- still targets `(2,2)`. The
second `solve_moves` call correctly refuses to let `S1` actually land there (`S2` is
genuinely stationary there on this call), so `S1` stays at `(3,2)` and `M` remains
blocked -- but exactly one re-match was *attempted*.

**Passed on the first run** -- no separate RED, since the single-round bound is
architecturally inherent (there is no loop construct in `yield_pass` to remove; it
detects, acts on at most one pair via `break 'outer`, and returns). To confirm this
wasn't a vacuous pass, hand-traced what a hypothetical SECOND call to `yield_pass` in
the same turn would do with this exact fixture's post-first-call state
(`cmd_by_id = {1: "MOVE 1 2 2", 2: "MOVE 2 1 2", 3: "CHOP 3"}`,
`landing = {1: (3,2), 2: (4,2)}`): `stationary` would be re-derived as just `{3}` (`S1`
now shows a `"MOVE "` command, even though it didn't actually move) -- so `best_progress`
for `M` with `S2` excluded from THIS narrower stationary set (`{}`) would show `M`
"unblocked" (since `S1`'s cell isn't in the set to exclude at all on this hypothetical
second call), and `(M, S2)` would be wrongly detected and acted on (`S2`'s value,
`72*BAND`-ish, is still `< 80*BAND`) -- a real cascade, confirming the single-round
guarantee is a call-discipline contract, not something `yield_pass` enforces
internally. This is why the CONTRACT paragraph was added to `yield_pass`'s doc comment
(see Design section above) rather than left implicit.

```
running 3 tests
test yield_corridor ... ok
test no_yield_when_blocker_outranks ... ok
test yield_single_round ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Gate results

1. **Baseline** (worktree post fast-forward, pre-edit): `cargo test --release` -> 58
   passed, 7 ignored, 0 failed (matches the task's stated baseline exactly).
2. **Refactor prep (commit `dad1e52`)** verified behavior-preserving BEFORE any new
   test was written: `cargo build --release` clean (same 5 pre-existing warnings, no new
   ones); `cargo test --release` -> 58 passed, 7 ignored, 0 failed (unchanged); `./target/
   release/equality target/release/bot target/release/bot 8 300 target/release/bot` ->
   `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
3. **RED / GREEN / flip-check**: see TDD section above.
4. **Full suite (final, commit `ffd03da`)**: `cargo build --release` clean, same 5
   pre-existing warnings (`PLUM` unused import in `printer_bot.rs`, `opp` unused
   variable in `boss_v3.rs`, `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`,
   `Strategy` unused import in `fastcheck.rs`), **no new warnings**. `cargo test
   --release` -> **61 passed** (58 baseline + 3 new), **7 ignored** (unchanged:
   `deny_probe` 1, `race_check` 1, `roam` 1, `tactics_scale` 4), **0 failed**. Per-suite
   counts, all unchanged from baseline except `yield_pass` (new): `idlefruit` 3,
   `motion_corridor` 2, `nanaflow` 2, `phase_factory` 1, `phase_hoard` 7,
   `phase_skeleton` 2, `pickloop` 4, `planner_solver` 3, `planner_tasks` 3, `race_check`
   2+1 ignored, `roam` 0+1 ignored, `sim_engine_tests` 26, `tactics_scale` 3+4 ignored,
   `deny_probe` 0+1 ignored, **`yield_pass` 3 (new)**.
5. **Self-determinism**: `./target/release/equality target/release/bot target/release/
   bot 8 300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command
   streams identical`.
6. **`tools/bundle.py`** (run from `rust/`): `src/botmain.rs -> target/refactor/
   bundled.rs: 94502 chars` (actual file: 96,035 B -- the usual multi-byte-UTF8 gap seen
   in every prior candidate report, e.g. em dashes). `grep -c` confirms exactly 1
   occurrence of `VERSION: &str = "1.43.0-yield"`. Champion base constants re-verified
   directly in the frozen bundled artifact: `STICKY: i64 = 6`, `DENY_W: i64 = 0`,
   `RACE_SHARE_PEN: i64 = 2`, `GE_MAX_TROLLS: i32 = 2`, `GE_FARM_R: i32 = 2`,
   `GE_FARM_MAX: usize = 12`, `GE_CHOP_R: i32 = 5` -- all match champion/live semantics;
   also re-confirmed the yield policy's comparison is `if vm > vs` (not the flip-check's
   `<`) in both `src/botmain/planner.rs` and the bundled artifact, and `git status
   --porcelain` was clean at the time of this check -- no leftover flip-check state.
7. **`rustc --edition 2021 -O`** on the bundled source (dot-free copy
   `bundled_check.rs`): exit 0 (SRC-COMPILE-OK).
8. **Bundle-inlining sanity**: `./target/release/equality target/refactor/
   bundled_check target/release/bot 8 300 target/release/bot` -> `EQUAL: 16 games (8
   seeds x 2 seats), all command streams identical`.
9. **`tools/minify.py`**: `94502 -> 49869 chars (52%)` (actual file: 49,869 B) -- 50.1%
   under the 100,000 B cap.
10. **`rustc --edition 2021 -O`** on the minified copy (dot-free copy `min_check.rs`):
    exit 0 (MIN-COMPILE-OK).
11. **Minified bin vs `target/release/bot`**: `EQUAL: 16 games (8 seeds x 2 seats), all
    command streams identical`.
12. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on
    the frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`
    (`diff`-verified: the only changed line is the `DEBUG` const itself). Bundled debug
    source: 96,034 B (1 byte shorter than the release bundled `.rs`, as expected --
    `false`->`true` is 1 byte shorter). Minified: `94501 -> 49868 chars (52%)` (1 byte
    shorter than the release `.min.rs`, matching the pattern seen on every prior
    candidate's probe). `rustc --edition 2021 -O` compile-check on the minified debug
    copy (dot-free copy `min_debug_check.rs`): exit 0 (DBG-COMPILE-OK). 2-seed local
    smoke: `./target/release/equality target/refactor/min_debug_check target/release/
    bot 2 300 target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command
    streams identical` (no crash; DEBUG only echoes to stderr, so stdout-parity holds).
13. **Champion-equality: N/A by design**, same framing as `v1.42.0-idlefruit`'s report --
    this candidate intentionally changes behavior (a lower-value stationary blocker now
    steps aside for a fully-blocked, higher-value mover). Self-determinism (gate 5) and
    the bundle/minify round-trip equalities (gates 8, 11) already establish full
    determinism and shuffle-invariance on the existing behavior corpus; that is a
    different, weaker guarantee than champion-equality and is not conflated with it
    here.
14. **Frozen artifacts re-verified byte-identical** to the exact gate-checked scratch
    copies (`cmp` against `target/refactor/{bundled,min,min_debug}_check.rs`) after
    copying to `cgauto/submissions/` and `data/candidates/v1.43.0-yield/` -- no drift
    between what was gated and what was frozen.

## Sizes

- `cgauto/submissions/v1.43.0-yield.rs`: **96,035 B** (bundled, comments retained).
- `cgauto/submissions/v1.43.0-yield.min.rs`: **49,869 B** (50.1% under the 100,000 B
  cap).
- `data/candidates/v1.43.0-yield/v1.43.0-yield.rs` / `.min.rs`: byte-identical
  (`cmp`-verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.43.0-yield/v1.43.0-yield.debug-probe.min.rs`: **49,868 B** (DEBUG=
  true; 1 byte shorter than the release `.min.rs`).

## Diffstat (vs base `6c661ee`)

```
rust/src/botmain.rs         |  19 ++-
rust/src/botmain/motion.rs  |  30 +++++
rust/src/botmain/planner.rs | 288 ++++++++++++++++++++++++++++++++++++++------
rust/tests/yield_pass.rs    | 251 ++++++++++++++++++++++++++++++++++++++  (new file)
4 files changed, 545 insertions(+), 43 deletions(-)
```

Three commits:
- `dad1e52` -- refactor(planner): extract joint_solve/render_one from assign; add
  motion::best_progress (behavior-preserving prep, verified via full suite + equality
  before any new test existed).
- `7c2d466` -- feat(yield): D2 yield-to-urgent -- blocker steps aside for a higher-value
  blocked mover (tests 1+2, real implementation, botmain.rs wiring, VERSION bump, the
  flip-check).
- `ffd03da` -- test(yield): pin the single-round bound (yield_single_round).

## Scope discipline

Touched: `rust/src/botmain.rs` (VERSION bump + the one new `if let` block around the
existing solve_moves landing-rewrite loop, which itself only changed from consuming
`landing` by value to borrowing it), `rust/src/botmain/motion.rs` (one new function,
`best_progress`, appended -- nothing existing edited), `rust/src/botmain/planner.rs`
(the `assign`-internals extraction into `Joint`/`joint_solve`/`render_one` -- mechanical,
behavior-preserving -- plus the new `YIELDS` counter/`yields()`/`parse_move_target`/
`yield_pass`), and the new `rust/tests/yield_pass.rs`. NOT touched: `candidates()` (the
per-troll band logic itself -- band values/gating/ordering are all untouched),
`tactics.rs`, any `GE_*`/`MB_*` constant, `STICKY`/`DENY_W`/`RACE_SHARE_PEN`, or any
existing test file.

## Concerns for the gatekeeper

- **This is a genuine behavior change** (not a pure refactor) -- champion-equality is
  N/A by design (see gate 13). The gate should watch for the yield mechanism firing on
  real maps: `@TFYIELD` (DEBUG-gated, in the debug-probe artifact) logs
  `t=<turn> blocker=<id> mover=<id>` each time it fires; `planner::yields()` gives a
  per-game running total if a harness wants a single number (not currently wired into
  any existing `@TFFARM`-style summary line -- it would need one added if the gate wants
  it printed automatically rather than grepped from `@TFYIELD` lines).
- **Expected live impact is narrow by construction**: the mechanism only fires when (a)
  a mover is FULLY blocked (zero progress, not just slowed) by (b) a stationary
  (non-MOVE) teammate whose task is worth strictly less. With `GE_MAX_TROLLS=2` live
  (the T-hand third troll is parked), the two-troll case is the only one that matters in
  practice; a full block at ms>=1 needs a fairly tight map (narrow paths / scarce camp
  cells), which is exactly the `v1.41.0-nopickloop`-era "scarce camp" scenario this
  codebase has hit before (see that candidate's `scarce_camp_park_leaves_drop_cell_free`
  test) -- so real fires are plausible but may be infrequent depending on map width. The
  boss/field mini-gate should watch wood delta for any regression (none expected -- a
  troll that WAS stationary-harvesting a real, non-doomed fruit only yields when a
  strictly higher-value mover is blocked by it, i.e. this should be strictly
  neutral-or-better on any turn it fires) and specifically look for `@TFYIELD` lines to
  confirm the mechanism is exercised at all on the gate's map sample -- if zero fires
  appear across the gate's games, that's a signal the scarce-corridor shape is rare on
  those particular maps, not that the code is broken (the unit tests already prove the
  mechanism itself works).
- **The band-52/band-75 BANANA double-candidate observation** from the flip-check (a
  BANANA tree generates both a standing Harvest candidate at band 75 and a self-targeting
  MoveTo candidate at band 52 for the very same cell) is pre-existing behavior from
  `v1.37.0-nanaflow`/`v1.41.0-nopickloop`-era `candidates()`, not something this
  candidate introduced -- flagged here only because the flip-check's failure output
  surfaced it concretely (`"MOVE 1 3 2"`, a self-target). It's harmless for `assign()`
  itself (band 75 always wins when both apply, since 75 > 52) and harmless for
  `yield_pass` under the CORRECT (non-inverted) comparison; noted for whoever next
  touches band 52/75 in case it's ever relevant.
- **`GE_MAX_TROLLS=2` and `T_SWITCH`/`Meta::Scale` are still dormant** (per the live
  `GE_META = Tempo` const) -- `yield_pass` runs unconditionally regardless of `Meta`/
  `Phase`, since the blocking shape it fixes (a stationary hard wall) is a motion-layer
  concern orthogonal to the tactics-layer phase machinery. No interaction expected, but
  worth knowing if a future Scale-meta gate ever fires this path under different troll
  counts.
