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

(Note superseded by commit `fcc96c2`, which regenerated the debug probe from the fixed bundle —
see the Mini-gate section below, which gates on that fresh probe.)

## Mini-gate (idlefruit): PASS — 2026-07-08 15:47

**Role: GATEKEEPER.** Candidate: `v1.42.0-idlefruit` = live `v1.41.0-nopickloop` base + planner
value band 38 ("idle-fruit"): an otherwise-idle troll harvests reachable ripe fruit instead of
parking, gated by `race()` so it never chases a doomed tree. Gate run against the probe frozen at
commit `fcc96c2` (post race-check fix `9948578`, debug-probe regenerated).

### Purity pre-check

Grepped `data/candidates/v1.42.0-idlefruit/v1.42.0-idlefruit.rs` directly:

| const | required | found | line |
|---|---|---|---|
| `VERSION` | contains "1.42.0-idlefruit" | `"1.42.0-idlefruit"` | 11 |
| `GE_CHOP_R` | `= 5` | `i32 = 5` | 1410 |
| `RACE_SHARE_PEN` | `= 2` | `i64 = 2` | 546 |
| `DENY_W` | `= 0` | `i64 = 0` | 537 |
| `STICKY` | `= 6` | `i64 = 6` | 525 |
| `GE_MAX_TROLLS` | `= 2` | `i32 = 2` | 1401 |

All six match champion semantics exactly — **no contamination**.

Probe freshness: `cmp <(sed 's/const DEBUG: bool = true;/const DEBUG: bool = false;/' …debug-probe.min.rs) …min.rs` → **files identical** (exit 0), confirming the probe differs from the release
build by the DEBUG flag only. Byte sizes 44,985 B (probe) vs 44,986 B (release) — the 1-byte gap
is exactly `"true"`(4) vs `"false"`(5), consistent with a clean DEBUG-only diff. Cross-checked
against git history: commit `fcc96c2` ("regenerate debug probe from fixed bundle") postdates the
race-check fix `9948578`, resolving this same report's earlier "not regenerated" note above (that
note described the pre-`fcc96c2` state). **Purity pre-check PASSES.**

### Boss mini-gate (6 games)

Collected via `collect_debug_games.py …debug-probe.min.rs boss 6` → gameIds 895490005, 895490023,
895490036, 895490058, 895490067, 895490076 (all 6/6 returned cleanly, distinct from the prior
v1.41.0-nopickloop gate's ids 895468000-895468151 still cached in the same directory).

| gameId | result | final turn | my wood | boss wood | delta |
|---|---|---|---|---|---|
| 895490005 | W | 300 | 48 | 52 | -4 |
| 895490023 | L | 300 | 51 | 66 | -15 |
| 895490036 | L | 300 | 40 | 59 | -19 |
| 895490058 | L | 300 | 32 | 42 | -10 |
| 895490067 | W | 300 | 50 | 53 | -3 |
| 895490076 | L | 300 | 42 | 40 | +2 |

2/6 wins (33%). `ramp.py --last 6`: t75 delta +3.2, t150 delta +2.7, t225 delta -1.2, **t300 delta
-8.2**; our avg final wood **43.8**; late-quarter (t225->300) gain us +10.5 vs opp +17.5.

**Crashes:** grep for panic/backtrace/fatal/unwrap/segv/timeout/invalid move/exception/traceback
across all 6 `.raw` files → 0 hits. Cross-checked with a second, independent method (full replay
fetch via `gameResult/findByGameId`, scanning every frame's `stderr` for both agents) → 0/6 panics
for us, 0/6 for the boss. Every game reaches t=300 (no truncation). **0/6 crashes.**

### Readout against thresholds

Reference (`v1.41.0-nopickloop` gate #3, clean base): wood 51.2 avg, t300 delta -12.3, 0 crashes.

- wood < 40 (FAIL floor)? **43.8 — PASS** (3.8 clear).
- delta worse than -15 (FAIL floor)? **-8.2 — PASS**, and actually 4.1 *better* than the reference's -12.3.
- any crash/timeout? **0/6 — PASS**.
- purity mismatch? **none — PASS**.
- WATCH: wood drop > 5 vs the 51.2 reference? **51.2 - 43.8 = 7.4 → WATCH TRIGGERED** — diagnosed below before finalizing the verdict, per the gate protocol.

### WATCH diagnosis: HARVEST/DROP telemetry + @TFFARM

**Telemetry-gap finding, reported plainly:** `@TFMOVE` (the only per-command debug line in our
stderr) is intentionally filtered to `cmds.iter().filter(|c| c.starts_with("MOVE "))` (source line
~1710) — it is a motion-block instrument and structurally cannot show HARVEST/DROP counts; grepping
our own `.raw` files for `HARVEST`/`DROP` returns **0 in every file**, for either candidate. This
is not a bug in this gate, but it means "grep our stderr for HARVEST/DROP" as literally specified
is not possible from the saved `.raw` artifacts (`collect_debug_games.py` only persists
`frames[*]['stderr']`, i.e. our own filtered debug text — never `stdout`, and never the opponent's
frames at all).

**Workaround used:** `gameResult/findByGameId` (the same real-replay endpoint `battles.py` uses for
rated ladder games) also serves these `TestSession/play` sandbox games and returns full
per-frame `stdout` for *both* agents. Fetched all 6 gameIds above, split each frame's `;`-joined
command string by verb (`MOVE`/`HARVEST`/`CHOP`/`DROP`/`PLANT`/`TRAIN`/`PICK`/`WAIT`/`MINE`/`MSG` —
confirming along the way that `CHOP` (wood-felling) and `HARVEST` (fruit-only) are genuinely
distinct commands in this ruleset, so `HARVEST+DROP` is a clean fruit-economy signal uncontaminated
by wood work):

| build | scope | us HARVEST | us DROP | **us H+D** | us CHOP | opp H+D | opp CHOP |
|---|---|---|---|---|---|---|---|
| v1.41.0-nopickloop (baseline, re-fetched, same 6-game gate ids 895468000-151) | 6 games | 115 | 176 | **291** (48.5/game) | 595 (99.2/game) | 508 | 841 |
| v1.42.0-idlefruit (candidate, this gate) | 6 games | 149 | 226 | **375** (62.5/game) | 581 (96.8/game) | 534 | 814 |
| **delta** | | +34 | +50 | **+84 (+29%)** | -14 (-2.4%, noise) | | |

This is exactly the predicted signature from the task brief: **HARVEST+DROP command count clearly
UP (+29%), CHOP (wood-felling) count flat within noise (-2.4%)** — the band is converting idle
turns to fruit activity without measurably displacing wood-chopping attempts.

`@TFFARM` end-of-game state, both batches (`farm`/`seeds`/`n`/`flaps`/`phase`):
- v1.42.0-idlefruit: flaps 5,5,15,6,6,8 (avg **7.5**); n=2 every game; farm 0-1; phase Tempo throughout.
- v1.41.0-nopickloop: flaps 8,6,6,10,14,12 (avg **9.3**); n=2 every game; farm 0-2; phase Tempo throughout.

No red flags — troll count, phase, and farm state are comparable across batches, and flaps
(target-flapping, a stability signal) is if anything slightly *better* in the candidate.

**Diagnosis:** the wood-drop pattern does **not** match the fruitbank failure mode (that mode
showed wood *and* chop activity collapsing together). Here CHOP attempts are flat and HARVEST+DROP
rose exactly as designed; `@TFFARM` shows no economy-health regression. The most likely driver is
ordinary n=6 map/opponent-draw variance — the v1.41.0-nopickloop gate #3 report itself flagged
~12-point batch-to-batch wood swings on identical code as expected noise at this sample size, and
7.4 sits inside that band. **WATCH resolved: not a structural regression; recommend the
arena-runner watch live wood if this ships, but this does not block the gate.**

### Field probe (2 games vs mikdiet, agentId 6480914 — harvest-economy archetype)

`collect_debug_games.py …debug-probe.min.rs 6480914 2` → gameIds 895490646, 895490657 (wins not
required for this leg).

| gameId | result | wood us-opp | score us-opp | margin | us H+D | opp H+D |
|---|---|---|---|---|---|---|
| 895490646 | L | 44-87 | 196-381 | -185 | 46 (H17/D29) | 137 (H76/D61) |
| 895490657 | L | 58-65 | 251-336 | -85 | 49 (H18/D31) | 188 (H112/D76) |

0/2 wins (not required, not a threshold). 0/2 crashes (grep + replay-stderr scan, same method as
above).

Totals: us H+D = 95 (avg **47.5/game**), opp H+D = 325 (avg **162.5/game**). Per the task's
reference framing ("typical champion losses to this cluster: opponents 91-307 HARVEST+DROP vs our
20-90"): mikdiet's 137/188 sit squarely in that opponent range, and **our 46/49 sit squarely in the
historical "our" 20-90 band too** — in this n=2 sample the band did **not** visibly lift us out of
the classic harvest-economy-loss signature, in contrast to the clear +29% lift seen vs the boss
pool. Plausible read: mikdiet's build (2nd troll by t2, 3-4 trolls by t15) keeps contested trees in
play longer, so `race()` correctly suppresses band 38 more often here than vs Boss 5's slower
build — or n=2 is simply too small to see the same effect. This is diagnostic only (step 4 carries
no pass/fail threshold); flagging for the analyst rather than treating it as a gate concern.

### Verdict: **PASS**

All four auto-fail legs clear cleanly (wood 43.8 ≥ 40; delta -8.2, better than both the -15 floor
and the -12.3 reference; 0/8 crashes across boss+field games via two independent detection
methods; purity clean). The one WATCH trigger (wood drop 7.4 > 5 vs reference) was investigated
per protocol and resolved as likely map-variance noise, not a structural regression — HARVEST+DROP
rose exactly as designed (+29%) while CHOP stayed flat and `@TFFARM` showed no economy damage.

**Recommendation:** hand off to the arena-runner for the live slot. Two notes to carry forward,
neither blocking: (1) the -8.2 t300 delta and 7.4 wood-avg drop vs reference are within known n=6
noise but worth a confirmatory larger-n boss read if a slot is cheap before submission; (2) the
field-probe HARVEST+DROP lift seen vs the boss pool (+29%) did not reproduce vs mikdiet-style
harvest-economy opponents in this 2-game sample — worth a wider field sample if the analyst wants
to confirm this lever also helps against that archetype, not just the boss.

**Telemetry gap for whoever owns the next probe rebuild:** `@TFMOVE`'s command filter (MOVE-only)
means HARVEST/DROP/CHOP/PLANT/etc. are invisible in our own stderr; this gate worked around it via
`gameResult/findByGameId` (confirmed to work on `TestSession/play` sandbox gameIds, not just rated
ladder games — undocumented before this gate). Consider either widening the `@TFMOVE` filter or
adding a dedicated `@TFCMD` verb-count line if this diagnostic is needed routinely, so future gates
don't need the ad hoc replay-fetch workaround.

## Arena verdict (2026-07-08, arena-runner)

Chained on the live v1.41.0-nopickloop baseline per MEASUREMENT POLICY v2 (deltas-only,
5h baseline horizon). Bracket (base) read confirmed the chain exactly matched the recorded
baseline before submitting.

- **Base/bracket:** 123/527 Gold @ 17.5, agentId `6543505`, read 15:42:31 MSK.
- **Submit:** `cgauto/api_submit.py cgauto/submissions/v1.42.0-idlefruit.min.rs` → SUBMIT-OK,
  15:42:40 MSK.
- **Read trajectory** (agentId `6543636` from the first read onward, confirming the candidate
  landed):
  - +20m (16:03:06): 180/527 @ **16.0**
  - +35m (16:17:54): 129/527 @ **17.3**
  - +50m (16:32:54): 127/527 @ **17.4**
  - Shape: dip → recover → flatten. Last-interval delta (+0.1) fell below the +0.2/read
    extension threshold, so the verdict was decided at +50m per the brief, no extension taken.
- **Delta:** 17.4 − 17.5 = **−0.1** — inside the v2 policy's `|delta| < 0.5` band.
- **Verdict: INCONCLUSIVE-KEEP.** The idle-fruit band 38 harvest-economy lever neither clearly
  helped nor hurt at this single-convergence sampling, despite the mini-gate's clean +29%
  HARVEST+DROP lift vs the boss pool (this arena read is against the live field pool, not the
  boss — consistent with the mini-gate's own flagged caveat that the harvest lift did not
  reproduce in the 2-game mikdiet field probe). Left live in the slot; becomes the new CHAINED
  BASELINE for the next candidate (valid ~5h, until ~21:33 MSK). NOT promoted — `api_submit.py`
  default stays `v1.36.0-race.min.rs` (v2 promotion needs +1.0 once or +0.5 twice; this reading
  is neither).
- **Goal gate (≤99):** did not fire — best rank this episode was 127/527.
- Full verdict-log entry: `docs/arena-queue.md` ("## Verdict log", newest-first).
