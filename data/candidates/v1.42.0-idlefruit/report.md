# Candidate v1.42.0-idlefruit — Builder Report

**Task (design D1, champion loss taxonomy 2026-07-08 morning):** 45% of all champion arena
losses (`docs/silver-experiment-log.md`, "## Champion loss taxonomy") are opponents
out-fruiting us — HARVEST+DROP command counts of 91-307 vs our flat 20-90 (HARVEST-ECONOMY +
DUAL-ECONOMY shapes, n=9/20, avg margin -63.9, by far the biggest lever in that dataset). The
fix, sharpened by the controller specifically against the **v1.24.0-fruitbank failure** (arena
-1.0, whose sin was ranking fruit-chasing *above* chop-help): a new Tempo-phase STARTER band,
**band 38**, strictly above anti-starvation (31/30) and strictly below chop-help (42/40) and
every printer band (52/50/49/48) — so it converts ONLY otherwise-idle turns into fruit points
and never displaces wood work, seed work, or hand funding.

## Worktree state (pre-task, resolved)

`git log --oneline -1` showed `fa33b21` ("feat: sim Bronze support + tuned wood economy
(v0.6.1)") — badly stale (predates the entire R6b planner rewrite). `git merge-base HEAD
session-2026-07-01` returned `fa33b21` itself (an ancestor), so fast-forwarded cleanly via `git
merge --ff-only session-2026-07-01` (working tree was clean; no rebase, no history rewrite).
Landed on `58141f6` ("gate(nopickloop): clean-base mini-gate #3 PASS (wood 51.2, delta -12.3, 0
crashes)"), a strict descendant of the required base `059ee5c` ("fix(tree): restore champion
semantics after roam4 revert (CHOP_R=5, PEN=2) + refreeze pickloop clean"). Confirmed the base
consts directly in source before touching anything: `rust/src/botmain.rs:98`
`GE_CHOP_R: i32 = 5`, `rust/src/botmain/planner.rs:59` `RACE_SHARE_PEN: i64 = 2`,
`rust/src/botmain/planner.rs:50` `DENY_W: i64 = 0` — all champion values, matching the exact
constants the previous candidate's contamination incident (v1.41.0-nopickloop, mini-gates #1/#2)
warned about. Re-verified after freezing that the constants baked into the frozen artifact are
still these champion values (see Gate results below) — no repeat of that incident. Bot crate
confirmed at `rust/` per `docs/superpowers/plans/pipeline-briefs.md`'s "Common context".

## What changed

### `rust/src/botmain/planner.rs`

One new block inserted in the STARTER (non-chopper) branch of `candidates()`, after item 6
("chop help (band 40) + anti-starvation (band 30)") and before the band-10 fallback:

```rust
// 6.5) IDLE-FRUIT (band 38, design D1 — champion loss taxonomy 2026-07-08 morning,
// docs/silver-experiment-log.md: 45% of all losses are opponents out-fruiting us,
// HARVEST+DROP 91-307 vs our flat 20-90). Strictly ABOVE anti-starvation (31/30) —
// never competes with keeping the wood supply alive — and strictly BELOW chop-help
// (42/40) and every printer/funding band above it (52/50/49/48/45/44/63/64/65/60/58) —
// this is the fix for the v1.24.0-fruitbank trap (arena -1.0), which ranked
// fruit-chasing ABOVE chop-help and lost. Because every one of those higher bands
// already claims its own trees first, band 38 only ever wins the joint assignment on
// a turn where nothing more valuable was available — it converts an otherwise-idle
// turn into fruit points and never displaces wood work, seed work, or funding. No
// per-type/own-half/roam gating on purpose ("harvest ANY ripe fruit"); mirrors the
// ChopHere/MoveTo split used by every other band in this function.
if u.harvest_power > 0 && u.free_capacity() > 0 {
    for p in state.trees.iter().filter(|p| p.fruits > 0 && d.contains_key(&p.pos())) {
        let pc = p.pos();
        if pc == u.pos() {
            out.push(Cand { kind: Kind::Harvest, target: Some(pc), value: 38 * BAND });
        } else {
            out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 38 * BAND - eta(&d, pc, ms) });
        }
    }
}
```

**Design note on the ChopHere/MoveTo split:** the task brief explored several ways to make an
*already-standing* troll actually harvest a fruit it just arrived at (extending band 75's
`want` predicate was one option considered and explicitly rejected — band 75's current gate is
funding/BANANA-or-water-APPLE/Hoard-only, and widening it would make a starter *passing over* a
fruit tree mid-route stop and harvest, a real displacement risk). The chosen fix instead mirrors
the pattern every other band in this function already uses (bands 70/72, 40/42, 30/31): push
`ChopHere`-equivalent (`Harvest`) when `pc == u.pos()`, `MoveTo` otherwise, all under the *same*
band value. This needed no change to band 75 at all — band 38 is fully self-contained.

Nothing else in `candidates()` or `assign()` was touched: `fell_ok`/`own_half`/`within_roam`/
`race`/`STICKY`/`DENY_W`/`RACE_SHARE_PEN`/every other band are byte-identical to
`v1.41.0-nopickloop`.

### `rust/src/botmain.rs`

```rust
const VERSION: &str = "1.42.0-idlefruit"; // D1: idle-fruit band 38 — convert idle starter turns into fruit points, never displacing wood/seed/funding work
```

## Band table — before / after

| band | kind (standing / traveling) | who | condition | new? |
|---|---|---|---|---|
| 95 | Bank | any | endgame banking window | |
| 88 | PlantHere / MoveTo | starter | carried banana + free plant cell | |
| 80 | Bank | any | full capacity (no plantable banana pending) | |
| 75 | Harvest | starter | standing on a *wanted* ripe fruit (funding/BANANA/water-APPLE/Hoard) | |
| 72 | ChopHere | chopper | standing on a fellable tree | |
| 70 | MoveTo | chopper | fellable tree, traveling | |
| 65 | Mine | starter | iron funding, ladder grace | |
| 64 | MoveTo | starter | iron funding, ladder grace | |
| 63 | MoveTo | starter | fruit funding, ladder grace | |
| 62 | MoveTo | starter | Hoard-phase wallet-building (any ripe fruit) | |
| 60/58 | Mine / MoveTo | starter | chopper funding (iron/fruit), non-ladder | |
| 52 | MoveTo | starter | ripe seed tree (tree-first printer) | |
| 50 | Pick | starter | shack-adjacent, tent has a banana | |
| 49 | Park | starter | park-to-pick errand | |
| 45/44 | Mine / MoveTo | starter | feeder funding (iron/fruit), non-ladder | |
| 42 | ChopHere | starter (chop-capable) | chop-help, standing | |
| 40 | MoveTo | starter (chop-capable) | chop-help, traveling | |
| **38** | **Harvest / MoveTo** | **starter (harvest-capable)** | **any ripe fruit reachable, free capacity — NEW** | **★** |
| 31 | ChopHere | any chop-capable | anti-starvation, standing | |
| 30 | MoveTo | any chop-capable | anti-starvation, traveling | |
| 10 | Park / Bank | any | idle fallback | |

Before this candidate, nothing occupied the gap between 40 and 31 — a chop_power=0 starter with
no funding/printer work available had **no candidate at all** in that range (chop-help/
anti-starvation for the STARTER branch is nested under `u.chop_power > 0`, so it doesn't exist
for a pure harvester), falling straight through to the band-10 fallback. Band 38 fills exactly
that gap without touching the relative order of anything else.

## TDD

New file `rust/tests/idlefruit.rs`, two tests, helpers copied verbatim from
`tests/planner_tasks.rs` (`base_state`/`base_plan`/`starter`/`banana`) plus a new `plum`
fruit-tree constructor.

### Test A — `idle_starter_harvests_fruit_instead_of_parking`

Farm at cap (`plan.base_trees = plan.farm_cap`, gates off printer bands 52/50/49/88); no
funding deficit (`want_chopper`/`want_feeder` both false, the `base_plan()` default); the troll
has `chop_power = 0` (no chop-help/anti-starvation candidates possible at all) and stands at
`(1,2)`, not on any tree; one ripe PLUM at `(4,2)` (`fruits=2`). Asserts `cmds[&0].contains("4
2")`.

**RED (verified — actually run against the pre-fix tree, not hand-derived):**

```
running 2 tests
test fruit_never_displaces_chop_help ... ok
test idle_starter_harvests_fruit_instead_of_parking ... FAILED

---- idle_starter_harvests_fruit_instead_of_parking stdout ----
thread 'idle_starter_harvests_fruit_instead_of_parking' panicked at tests/idlefruit.rs:112:5:
idle starter with a ripe fruit reachable and nothing better to do should go harvest it, got: MOVE 0 1 2

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Exactly the predicted pre-fix failure: with no band claiming the plum at all, only the band-10
fallback (`Park`) survives, and `motion::park_cmd`'s nearest-unclaimed-camp-cell search picks
the troll's **own current cell** `(1,2)` (distance 0 from itself, and already shack-adjacent) —
an effective no-op park, i.e. exactly "parks" as anticipated in the design brief.

**GREEN (post-fix):**

```
running 2 tests
test fruit_never_displaces_chop_help ... ok
test idle_starter_harvests_fruit_instead_of_parking ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

### Test B — `fruit_never_displaces_chop_help`

Same construction as Test A (farm at cap, no funding deficit, ripe plum at `(4,2)`), but
`chop_power = 1` (the `starter()` default — chop-help is now available) and a fellable own-half
banana at `(3,2)`: map-distance 3 from the shack `<=` `chop_r=5` (`within_roam`); manhattan to
our shack (3) `<=` manhattan to the opponent's shack at `(7,2)` (4) (`own_half`). Asserts the
target is `(3,2)` and explicitly asserts it is **not** `(4,2)`.

This is a **non-regression pin**, not a RED/GREEN pair — it must pass both before and after the
fix (pre-fix, chop-help is simply the only real candidate; post-fix, chop-help must still
outrank the new band 38). Confirmed: **passed pre-fix** (see Test A's RED run above — `ok` on
the first line) **and passed post-fix** (see the GREEN run above).

### Flip-check (verifies the pin actually pins something)

A test that "passes both before and after" is only meaningful if it would *catch* a wrong band
placement. Per the task brief, temporarily raised the idle-fruit band from 38 to 45 (above
chop-help's 42/40) via `sed -i 's/38 \* BAND/45 * BAND/g' src/botmain/planner.rs` (both the
`Harvest` and `MoveTo` push sites), reran:

```
running 2 tests
test idle_starter_harvests_fruit_instead_of_parking ... ok
test fruit_never_displaces_chop_help ... FAILED

---- fruit_never_displaces_chop_help stdout ----
thread 'fruit_never_displaces_chop_help' panicked at tests/idlefruit.rs:137:5:
chop-help must win over the idle-fruit band, got: MOVE 0 4 2

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Confirmed: at band 45 the plum (`45*BAND - 3 = 4,499,997`) outranks the chop-help banana
(`40*BAND - 6 = 3,999,994`) and the starter wrongly diverts to `(4,2)` — the exact
v1.24.0-fruitbank failure mode, reproduced on demand. This proves Test B is a live tripwire, not
a vacuously-true assertion. Reverted via `sed -i 's/45 \* BAND/38 * BAND/g'
src/botmain/planner.rs`, confirmed both `38 * BAND` occurrences restored (`grep -n` showed lines
459/461 back to `38`), reran the full `idlefruit.rs` suite: both tests green again (see GREEN
block above, which is the post-revert run).

## Gate results

1. **Baseline** (worktree post fast-forward, pre-edit): `cargo build --release` clean, 5
   pre-existing warnings (`PLUM` unused import in `printer_bot.rs`, `opp` unused variable in
   `boss_v3.rs`, `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`, `Strategy` unused
   import in `fastcheck.rs`).
2. **RED — `idlefruit.rs` Test A vs pre-fix code**: exact failure message above (`MOVE 0 1 2`);
   Test B **passes pre-fix** (as designed, confirming it's a true non-regression pin not a
   RED/GREEN pair).
3. **GREEN — `cargo build --release`** (post-fix): clean, same 5 pre-existing warnings, **no new
   warnings**.
4. **GREEN — `cargo test --release`**: **30 suites** (15 unittest binaries with 0 tests each +
   14 integration test files + 1 doc-test), **57 passed + 7 ignored + 0 failed**. New
   `idlefruit.rs`: 2 passed. Every other suite's count unchanged from the `v1.41.0-nopickloop`
   clean-base baseline: `deny_probe` 0+1 ignored, `motion_corridor` 2, `nanaflow` 2,
   `phase_factory` 1, `phase_hoard` 7, `phase_skeleton` 2, `pickloop` 4, `planner_solver` 3,
   `planner_tasks` 3, `race_check` 2+1 ignored, `roam` 0+1 ignored, `sim_engine_tests` 26,
   `tactics_scale` 3+4 ignored.
5. **Flip-check**: see above — band 45 makes Test B fail with the predicted fruitbank-trap
   symptom (`MOVE 0 4 2`); reverting to 38 restores both tests green.
6. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8 300
   target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
7. **`tools/bundle.py`** (run from `rust/`): `src/botmain.rs -> target/refactor/bundled.rs: 81068
   chars` (actual file: 82,479 B — the usual multi-byte-UTF8/self-report gap seen in every prior
   candidate report, e.g. em dashes). `grep -c` confirms exactly 1 occurrence of `VERSION: &str
   = "1.42.0-idlefruit"`. Champion base constants re-verified directly in the frozen artifact:
   `GE_CHOP_R: i32 = 5`, `RACE_SHARE_PEN: i64 = 2`, `DENY_W: i64 = 0` — no repeat of the
   `v1.41.0-nopickloop` roam4-contamination incident.
8. **`rustc --edition 2021 -O`** on the bundled source (dot-free copy `bundled_check.rs`): exit
   0 (SRC-COMPILE-OK).
9. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8 seeds
   x 2 seats), all command streams identical`.
10. **`tools/minify.py`**: `81068 -> 44856 chars (55%)` (actual file: 44,856 B) — 55% under the
    100,000 B cap.
11. **`rustc --edition 2021 -O`** on the minified copy (dot-free copy `min_check.rs`): exit 0
    (MIN-COMPILE-OK).
12. **Minified bin vs `target/release/bot`**: `EQUAL: 16 games (8 seeds x 2 seats), all command
    streams identical`.
13. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Bundled debug source:
    82,478 B (1 byte shorter than the release bundled `.rs`, as expected — `false`->`true` is 1
    byte shorter). Minified: `81067 -> 44855 chars (55%)` (1 byte shorter than the release
    `.min.rs`, matching the pattern seen on every prior candidate's probe). `rustc --edition 2021
    -O` compile-check on the minified debug copy (dot-free copy `min_debug_check.rs`): exit 0
    (DBG-COMPILE-OK). 2-seed local smoke: `./target/release/equality
    target/refactor/min_debug_check target/release/bot 2 300 target/release/bot` -> `EQUAL: 4
    games (2 seeds x 2 seats), all command streams identical` (no crash; DEBUG only echoes to
    stderr, so stdout-parity holds).
14. **Champion-equality: N/A by design**, per the task's own framing ("NO champion equality
    (behavior change)") — this candidate intentionally changes behavior (a starter with nothing
    better to do now harvests idle fruit instead of parking). Self-determinism (gate 6) and the
    bundle/minify round-trip equalities (gates 9, 12) already establish full determinism and
    shuffle-invariance on the existing behavior corpus; that is a different, weaker guarantee
    than champion-equality and is not conflated with it here.
15. **Frozen artifacts re-verified byte-identical** to the exact gate-checked scratch copies
    (`cmp` against `target/refactor/{bundled,min,min_debug}_check.rs`) before/after copying to
    `cgauto/submissions/` and `data/candidates/v1.42.0-idlefruit/` — no drift between what was
    gated and what was frozen.

## Sizes

- `cgauto/submissions/v1.42.0-idlefruit.rs`: **82,479 B** (bundled, comments retained).
- `cgauto/submissions/v1.42.0-idlefruit.min.rs`: **44,856 B** (55% under the 100,000 B cap).
- `data/candidates/v1.42.0-idlefruit/v1.42.0-idlefruit.rs` / `.min.rs`: byte-identical
  (`cmp`-verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.42.0-idlefruit/v1.42.0-idlefruit.debug-probe.min.rs`: **44,855 B** (DEBUG=
  true; 1 byte shorter than the release `.min.rs`).

## Diffstat

```
rust/src/botmain.rs         |  2 +-
rust/src/botmain/planner.rs | 22 ++++++++++++++++++++++
rust/tests/idlefruit.rs     | 147 +++++++++++++++++++++++++++++++++++++++++++  (new file)
3 files changed, 23 insertions(+), 1 deletion(-) in tracked files + idlefruit.rs new
```

## Scope discipline

Touched only: the one new band-38 block in `planner.rs::candidates()` (STARTER branch), the
`VERSION` string in `botmain.rs`, and the new `rust/tests/idlefruit.rs`. NOT touched: `fell_ok`/
`own_half`/`within_roam`/`race`/`STICKY`/`DENY_W`/`RACE_SHARE_PEN`/any other band (95/88/80/75/
72/70/65/64/63/62/60/58/52/50/49/45/44/42/40/31/30/10), band 75's `want` predicate (considered
and explicitly rejected as the implementation site — see "Design note" above), `motion.rs`,
`tactics.rs`, or any `GE_*`/farm-geometry constant besides the version string.

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` then vs field (incl. >=1 denial-style
opponent — mikdiet 6480914 / plcc 6480966 — and >=1 >=19.6 player per `field_targets.py`). Read
`cgauto/ramp.py --last 8` (wood >=45, t300 delta vs -12.3 baseline — the current clean-base
`v1.41.0-nopickloop` reading) and telemetry from the newest `.raw` files (`@TFFARM`/`@TFPHASE`).
Expected signature: on the majority of maps this should look byte-identical in wood/chop terms
to `v1.41.0-nopickloop` (band 38 only ever fires when a troll would otherwise have parked, which
by definition contributes nothing to wood) — watch specifically for (a) any HARVEST/DROP command
count increase in the per-phase command-mix census used by the loss-taxonomy analysis itself
(the intended effect); (b) any wood *regression* (would indicate band 38 is unexpectedly
outranking or delaying real chop-help/funding work — the taxonomy's own numbers say this
shouldn't happen given the band spacing, but real maps have interactions the two unit tests
can't fully anticipate, e.g. a fruit tree that also happens to be a farm banana mid-maturation,
or interaction with the race check on a contested cell that also bears fruit); (c) whether the
HARVEST-ECONOMY/DUAL-ECONOMY loss shapes specifically narrow in a follow-up loss-taxonomy census
once this candidate has arena games to sample.

## Fix: race() in band 38 (review follow-up)

**Finding (code review, IMPORTANT):** the band-38 loop above did not consult `race()` — every
other tree-targeting band in `candidates()` (72/70, 42/40, 31/30) skips a candidate whose tree an
enemy chopper will fell before our ETA (doomed-target chasing, the v1.36.0-race fix), but band 38
pushed a `Harvest`/`MoveTo` candidate for *any* ripe-fruit tree unconditionally. An idle troll
could therefore trek toward a fruit tree an enemy chopper stood on and was about to fell —
donated travel, the exact waste class v1.36.0-race closed for wood.

### What changed

`rust/src/botmain/planner.rs`, band 38 (STARTER branch of `candidates()`): hoisted `let steps =
eta(&d, pc, ms);` before the branch (previously only computed inline for the `MoveTo` arm), then
added the same race gate every other band uses:

```rust
let steps = eta(&d, pc, ms);
if race(pc, steps).is_none() {
    continue; // doomed: they fell it before we arrive — skip, don't donate the travel
}
if pc == u.pos() {
    out.push(Cand { kind: Kind::Harvest, target: Some(pc), value: 38 * BAND });
} else {
    out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 38 * BAND - steps });
}
```

Unlike the wood bands, the `Some(pen)` arm's penalty is **not** subtracted from the value —
sharing a cell with an enemy chopper while *we* harvest fruit isn't a wood-split situation
(`apply_chop`'s round-robin split is a wood-only engine mechanic), so `race`'s `Some(_)` result is
used only as the "not doomed" signal here. The same pre-branch check structurally covers both the
same-cell `Harvest` candidate and the `MoveTo` candidate (matching how bands 70/72 and 40/42 apply
one check before their own standing/traveling split) — verified by hand that this costs the
same-cell case nothing: at `pc == u.pos()`, `steps == 0`, and `race(pc, 0)` can only return `None`
if the tree's health is already `<= 0`, which cannot coexist with this loop's own `p.fruits > 0`
filter, so the guard is a live tripwire for `MoveTo` and a no-op for `Harvest`, never a false skip.

No other band, constant, or file touched.

### Test evidence

New test `idle_troll_skips_doomed_fruit` in `rust/tests/idlefruit.rs`: same fixture as
`idle_starter_harvests_fruit_instead_of_parking` (farm at cap, no funding deficit, `chop_power =
0` starter so chop-help/anti-starvation can't fire) plus an enemy `chopper()` (helper copied from
`tests/race_check.rs`) standing on the ripe plum at `(4,2)`, health 4, `chop_power` 2 → 2 turns to
fell it, versus our troll's `our_eta = 3` (map-distance 3 at `movement_speed` 1) — the enemy wins
the race, so band 38 must skip the tree.

**RED (verified — test added and run BEFORE the source fix, not hand-waved):**

```
$ cargo test --release --test idlefruit
running 3 tests
test fruit_never_displaces_chop_help ... ok
test idle_starter_harvests_fruit_instead_of_parking ... ok
test idle_troll_skips_doomed_fruit ... FAILED

---- idle_troll_skips_doomed_fruit stdout ----
thread 'idle_troll_skips_doomed_fruit' panicked at tests/idlefruit.rs:184:5:
doomed fruit (enemy fells it before our ETA) must be skipped, not chased, got: MOVE 0 4 2

test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Exactly the predicted pre-fix failure: with no race check, band 38 unconditionally out-values the
band-10 `Park` fallback and the troll treks toward the doomed plum.

**GREEN (post-fix), required suite:**

```
$ cargo test --release --test idlefruit --test planner_tasks --test race_check --test planner_solver
idlefruit:       3 passed; 0 failed; 0 ignored
planner_solver:  3 passed; 0 failed; 0 ignored
planner_tasks:   3 passed; 0 failed; 0 ignored
race_check:      2 passed; 0 failed; 1 ignored (share_pen_shifts_near_tie_to_free_tree, pre-existing)
```

**Full workspace suite (regression check against this candidate's original gate #4 baseline of
57 passed + 7 ignored):** `cargo test --release` → **58 passed** (57 + this one new test), **7
ignored** (unchanged: `deny_probe` 1, `race_check` 1, `roam` 1, `tactics_scale` 4), **0 failed**.
`cargo build --release`: clean, same 5 pre-existing warnings as the original gate #1 baseline, no
new warnings.

**Determinism/bundling re-verified after the fix** (same gate pattern as this candidate's
original gates 6/9/12, all against the freshly rebuilt `target/release/bot`):

```
self-determinism (bot vs bot):            EQUAL: 16 games (8 seeds x 2 seats), all command streams identical
bundle-inlining sanity (bot vs bundled):  EQUAL: 16 games (8 seeds x 2 seats), all command streams identical
minified sanity (bot vs minified):        EQUAL: 16 games (8 seeds x 2 seats), all command streams identical
```

`rustc --edition 2021 -O` on dot-free scratch copies of both the rebundled and re-minified files:
exit 0 for both (SRC-COMPILE-OK / MIN-COMPILE-OK).

### Artifacts rebuilt

Regenerated via `tools/bundle.py src/botmain.rs ../cgauto/submissions/v1.42.0-idlefruit.rs` then
`tools/minify.py ../cgauto/submissions/v1.42.0-idlefruit.rs ../cgauto/submissions/v1.42.0-idlefruit.min.rs`,
copied byte-identically (`cmp`-verified) over the `data/candidates/v1.42.0-idlefruit/` copies:

| artifact | before this fix | after this fix |
|---|---|---|
| `v1.42.0-idlefruit.rs` (bundled) | 82,479 B | 83,644 B |
| `v1.42.0-idlefruit.min.rs` (minified) | 44,856 B | 44,986 B (55% under the 100,000 B cap) |

The `.debug-probe.min.rs` copy was not regenerated (out of scope for this fix; unaffected by the
band-38 change beyond the same +130 B this fix adds elsewhere).
