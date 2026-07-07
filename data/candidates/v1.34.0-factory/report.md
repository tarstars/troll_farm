# Candidate v1.34.0-factory — Builder Report

**Task:** Task 4 (B3) — factory bands: after `T_SWITCH` the hoard gates naturally reopen (already
true since Task 3), and the farm capacity grows (12→20) so the plant-and-fell loop has room.
**Role executed:** BUILDER only (`.superpowers/sdd/task-4-brief.md` Steps 1–6 /
`docs/superpowers/plans/pipeline-briefs.md` builder-brief steps 1–7, TDD-style), per the
dispatching agent's explicit resolutions of the brief's ambiguities. Step 7 ("gatekeeper, Scale
build" — boss games + invariant checks) is a **separate role**, out of scope here; see §7.
**Base tree:** working tree at the start of this task = `v1.33.0-hoard` (Task 3, hoard bands +
Scale ladder), HEAD `6c67d2c`, confirmed clean before edits. Champion artifact
`cgauto/submissions/v1.28.3-sticky6.min.rs` — read only, never touched.

## 1. What changed

Exactly the items the dispatching agent's binding resolutions specified, nothing else:

1. **`farm_cap` becomes phase-aware** in `rust/src/botmain/tactics.rs` `plan()`:
   `let farm_cap = if phase == Phase::Factory { 20 } else if econ_b { 20 } else { GE_FARM_MAX };`
   — written exactly as the brief's Step 3 shows. Hoard and Tempo are unchanged (`econ_b` is a
   permanent `false` const, so both fall through to `GE_FARM_MAX` = 12). Factory needs no band
   suppression changes — the Hoard-only gates in `planner.rs` (`plan.phase == Phase::Hoard`)
   already treat Factory exactly like Tempo (reopened), so **`planner.rs` was not touched at
   all**, matching the brief's "Interfaces" line verbatim.
   - Mechanical prerequisite: `phase` was previously computed *after* the farm-config block
     (right before constructing `Plan`). Since `farm_cap` now needs `phase`, the single
     `let phase = phase_for(super::GE_META, state.turn);` binding moved up to immediately before
     the farm-config block; the now-redundant later binding was removed (the `Plan { …, phase }`
     struct literal reuses the same binding). `phase_for` is a pure function of `(meta, turn)`
     with no dependency on anything computed in between, so the reordering has zero effect on any
     other field.
2. **Comment fix (Task-3-review item, in scope per the resolution):** the Scale-branch comment
   claiming "no t3 chopper at all" was misleading — `SCALE_LADDER` slot 2 (`(2,2,0,2)`, chop=2)
   **is** a real chopper, trained once `n` reaches 3 hands at `t>=110`. Reworded to say the early
   *adaptive* (turn-1) chopper is replaced by the ladder itself, whose final slot trains a real
   chopper at `t>=110`.
3. **`VERSION`** → `"1.34.0-factory"` in `rust/src/botmain.rs`.
4. **New test** `rust/tests/phase_factory.rs` — helpers (`base_state`/`starter`/`chopper`/
   `banana`) copied VERBATIM from `tests/phase_hoard.rs`; `base_plan()` copied with two field
   changes: `farm_cap: 20` (was 12) and `phase: Phase::Factory` (was `Phase::Hoard`). Test body
   (`factory_plants_and_fells`) copied verbatim from the brief's Step 1: banana(1,1,2) sits at
   map-distance 2 from the shack (0,2) = inside the radius-2 farm; the banana-carrying starter
   must PLANT/MOVE-to-plant, the chopper standing on the size-2 farm banana must `CHOP 2`.

`git diff --stat` on the source tree: exactly `rust/src/botmain.rs` (1 line) +
`rust/src/botmain/tactics.rs` (11 insertions / 5 deletions), plus the one new test file.

## 2. TDD process — the vacuous-pass finding (foreseen by the brief) and how it was resolved

Followed the brief's Steps 1–2 literally:

1. **Wrote the test first** (`rust/tests/phase_factory.rs`, brief's exact test body).
2. **Ran it before touching `tactics.rs`:** `cargo test --release --test phase_factory`
   → `test factory_plants_and_fells ... ok` — **it PASSED, not failed.**

This is exactly the contingency the dispatching agent's resolution called out by name: *"If both
assertions already pass with a hand-built Plan (they may — Factory reopens everything)…"*. Root
cause: the test's `assign(&st, &base_plan(), …)` never invokes `tactics::plan()` — it hands
`assign()` a **literal, hand-built `Plan`** with `farm_cap: 20` and `phase: Phase::Factory`
already baked in by the test helper itself. Two independent facts make the assertions pass
regardless of whether the `tactics.rs` change exists yet:
- `Phase::Factory` and the `farm_cap: usize` field both already existed (Task 2), so the struct
  literal compiles and runs against the pre-B3 `planner.rs` unchanged.
- `planner.rs`'s only phase-conditional logic is `hoard = plan.phase == Phase::Hoard`; since
  `Factory != Hoard`, Factory already behaved identically to Tempo *before this task* —
  confirming the brief's own "Interfaces" claim that planner.rs needs zero changes.
- The test's `base_trees: 0` (hardcoded) is `< 12` and `< 20` alike, so this test can't even
  distinguish the two `farm_cap` values — it exercises "does Factory reopen the plant/fell
  bands," which was already true, not "is farm_cap 20."

Per the resolution's explicit fallback: *"the failing-first requirement applies to a SECOND,
tactics-level test… SKIP this if `plan()` can't be driven to Factory without `GE_META=Scale` at
compile time; in that case document in the report that the farm_cap line is covered by inspection
+ the frozen Scale probe, and keep the behavioral test. Do not contort the code to make a test
possible."*

**Checked and confirmed the skip condition holds:** `GE_META` is a plain `const` in `botmain.rs`
(`const GE_META: tactics::Meta = tactics::Meta::Tempo;`), read directly inside `tactics::plan()`
as `super::GE_META` — no parameter, thread-local, or env-var injection point exists. An external
integration test in `rust/tests/` cannot drive `plan()` into the Scale/Factory branch without
either (a) editing the live constant (a behavior change that would break the very
Tempo-inertness this task is gated on), or (b) refactoring `plan()` to accept an injected `Meta`
(explicitly the "contort the code" case the resolution forbids). Also checked the resolution's
other fallback: `tests/phase_skeleton.rs` has **no** corridor-style `State` construction to copy
(it only calls `phase_for` directly, no `State`/`Plan` at all), closing that path too.

**Decision: skipped the second tactics-level test**, kept the single behavioral test as
specified, and covered the actual `farm_cap` phase-aware line by three independent,
non-code-contorting means:
1. **Inspection** — the new line is a single readable conditional keyed on the same `phase`
   binding that Task 2's `phase_skeleton.rs` already unit-tests at the exact boundary
   (`phase_for(Meta::Scale, T_SWITCH) == Phase::Factory`, `T_SWITCH - 1` still `Hoard`). `phase`
   is the *only* new input the `farm_cap` line depends on, and that input's boundary correctness
   is already proven; the one-line consequence (`Factory => 20`) follows by inspection.
2. **A fresh Scale-mode DEBUG probe built from this task's own frozen candidate** (not reused
   from Task 3 — that one predates this diff): `sed` `DEBUG`→`true` and `GE_META`→`Meta::Scale`
   on `cgauto/submissions/v1.34.0-factory.rs`, rustc-compile-checked (exit 0, both the full and
   the minified copy), then smoke-tested over the raw stdin/stdout wire protocol for **145
   synthetic turns** (6x6 empty map, one starter troll, no network). The phase telemetry
   (`@TFFARM`, every 5 turns) flips cleanly and the process never crashes (exit 0):
   ```
   @TFFARM t=135 farm=0 seeds=0 n=1 flaps=0 phase=Hoard
   @TFFARM t=140 farm=0 seeds=0 n=1 flaps=0 phase=Factory
   @TFFARM t=145 farm=0 seeds=0 n=1 flaps=0 phase=Factory
   ```
   (all checkpoints t=5..135 read `phase=Hoard`; verified on the full AND the minified probe
   binary). `@TFFARM` doesn't print `farm_cap` itself, so this confirms the end-to-end *wiring*
   (`GE_META=Scale` → `phase_for` → `plan()`'s `phase` binding, the same binding the new
   `farm_cap` line reads) rather than the field value directly — combined with point 1 this is
   sufficient without widening `decide_elite`'s debug print (out of this task's one-line scope).
   Probe frozen to `data/candidates/v1.34.0-factory/v1.34.0-factory.scale-debug-probe.min.rs`
   (41,570 bytes, compile-checked) for the gatekeeper.
3. **The behavioral test** (kept, green) plus the label-matched 50-game equality gate (§3,
   Gate 8) prove the Tempo side of the same `if/else if/else` is an exact no-op — the only
   branch NOT covered by equality is the one this task adds, and that branch is covered by
   (1)+(2).

## 3. Gate results (pipeline-briefs.md builder-brief steps 2–7)

All commands run with cwd = `/home/tarstars/prj/troll_farm/rust` unless noted. Gates were run
after implementation and **re-run end-to-end on 2026-07-07 after a session interruption** to
re-record outputs against the final frozen source; both passes produced identical results (the
numbers below are from the final re-run).

### Gate 1 — `cargo build --release`
`Finished release [optimized] target(s)`. 0 compile errors. Only pre-existing warnings (unused
`PLUM` import in `printer_bot.rs`, unused `opp` in `boss_v3.rs`, unused `HARVESTER` consts in
`silver_boss.rs`/`mybot.rs`, unused `Strategy` import in `fastcheck.rs`) — identical set to
Task 3's report; none touch this diff.

### Gate 2 — `cargo test --release`
`grep -c "test result: ok"` → **23** suites (was 22 after Task 3, +1 for the new
`phase_factory.rs` suite). `grep -c FAILED` → **0**. Sum of all `N passed` → **39** individual
tests (was 38, +1). New suite's own output:
```
Running tests/phase_factory.rs
running 1 test
test factory_plants_and_fells ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```
All pre-existing suites unaffected, including `tests/phase_hoard.rs` (2 passed) and
`tests/phase_skeleton.rs` (2 passed).

### Gate 3 — self-determinism
```
./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
```
`EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`

### Gate 4 — bundle
```
uv run --no-sync python tools/bundle.py
```
`src/botmain.rs -> target/refactor/bundled.rs: 63111 chars (gate with rustc + equality + minify)`
`cmp target/refactor/bundled.rs ../cgauto/submissions/v1.34.0-factory.rs` → byte-identical
(the frozen artifact matches the final source exactly).

### Gate 5 — compile the bundled (dot-free) copy
`rustc --edition 2021 -O <scratch copy of v1.34.0-factory.rs>` → exit 0, no errors.

### Bonus gate (bundle-inlining sanity, per `bundle.py`'s own docstring)
```
./target/release/equality <bundled_bin> target/release/bot 8 300 target/release/bot
```
`EQUAL: 16 games (8 seeds x 2 seats), all command streams identical` — bundling introduced no
drift vs the lib-built binary.

### Gate 6 — minify
```
uv run --no-sync python tools/minify.py target/refactor/bundled.rs ../cgauto/submissions/v1.34.0-factory.min.rs
```
`63111 -> 41571 chars (65%)`. `wc -c` confirms **41571 bytes** — 58.4% under the 100,000-byte
cap. Re-minified from the re-bundled source on 2026-07-07 and `cmp`-verified byte-identical to
the frozen `.min.rs`.

### Gate 7 — compile the minified (dot-free) copy
`rustc --edition 2021 -O <scratch copy of v1.34.0-factory.min.rs>` → exit 0, no errors.

### Gate 8 — **THE gate**: flag-off equality vs the champion (`v1.28.3-sticky6.min.rs`)

Per the pipeline-briefs.md common context ("equality gates compare against
`cgauto/submissions/v1.28.3-sticky6.min.rs`") and the label-match technique from Task 2/3's
reports (VERSION strings differ only in the turn-1 `MSG` command, which the black-box command
comparison would otherwise flag as a trivial divergence):
```
cp cgauto/submissions/v1.28.3-sticky6.min.rs <scratch>/champ.rs
rustc --edition 2021 -O <scratch>/champ.rs -o <scratch>/champ_bin
sed 's/1\.34\.0-factory/1.28.3-sticky6/' target/refactor/bundled.rs > <scratch>/lm.rs
rustc --edition 2021 -O <scratch>/lm.rs -o <scratch>/lm_bin
./target/release/equality <scratch>/champ_bin <scratch>/lm_bin 25 300 <scratch>/champ_bin
```
Decisive line: **`EQUAL: 50 games (25 seeds x 2 seats), all command streams identical`**

This proves the task's central claim: with `GE_META = Meta::Tempo` live, moving the `phase`
binding earlier, adding the Factory arm to `farm_cap`, and rewording the Scale-branch comment
changes **nothing**, byte-for-byte, across every command line CG's stdout protocol would carry,
for 50 full games — Tempo never reaches `Phase::Factory` (`phase_for(Tempo, _) == Phase::Tempo`
always, proven in `phase_skeleton.rs`), so the new branch is dead code on the live path.

**Extra verification (rigor, mirroring Task 3's precedent):** diffed every `const` declaration
between the champion `.min.rs` and the new bundle (`grep -oE "const [A-Z_0-9]+: [^=]+= [^;]+;" …
| sort | diff`). The only differences are **additive and pre-existing from Tasks 2/3**
(`GE_META`, `SCALE_LADDER`, `SCALE_MIN_TURN`, `T_SWITCH`) plus the expected `VERSION` string. No
pre-existing tunable const drifted, and this task introduced **zero new consts** (the change is a
conditional expression, not a tunable).

## 4. Artifact sizes

| Artifact | Bytes | Notes |
|---|---|---|
| `cgauto/submissions/v1.34.0-factory.rs` (full bundled) | 64,430 | disk bytes > `bundle.py`'s 63,111 *chars* — multi-byte UTF-8 in comments, same pattern as every prior frozen artifact. |
| `cgauto/submissions/v1.34.0-factory.min.rs` (minified, submission) | 41,571 | matches `minify.py`'s char count exactly (pure ASCII post-minification) — 58.4% under the 100 KB cap. |

Both frozen to `cgauto/submissions/` and duplicated to
`data/candidates/v1.34.0-factory/{v1.34.0-factory.rs,v1.34.0-factory.min.rs}` (`cmp`-verified
identical to the submissions copies). Sanity-verified in both frozen copies:
`const VERSION: &str = "1.34.0-factory"` (1 hit each), the phase-aware `farm_cap` line present
verbatim in both (`grep -n "farm_cap = if phase"`).

## 5. Anomalies

- **The TDD "failing-first" step did not fail** — see §2. Explicitly foreseen and pre-authorized
  by the dispatching agent's resolution (down to the phrase "they may — Factory reopens
  everything"); the resolution's fallback path was followed to the letter and the skip reasoning
  is recorded rather than silently omitted.
- **Session interruption:** the original builder session was cut by a connection error after the
  artifacts were frozen but before the report/commit landed. All gates were re-run from the
  restored session on 2026-07-07 against the final tree; re-bundle/re-minify were `cmp`-verified
  byte-identical to the frozen artifacts (no drift between the interrupted pass and the final
  source).
- No other anomalies. Build/tests passed clean on the first attempt after implementation; no
  flaky gate.

## 6. Scope discipline

- Champion artifact (`v1.28.3-sticky6.*`) — read only, never written.
- Only `rust/src/botmain.rs` and `rust/src/botmain/tactics.rs` modified in the source tree
  (11 insertions / 5 deletions in tactics.rs, 1-line VERSION bump in botmain.rs);
  `rust/tests/phase_factory.rs` added. `rust/src/botmain/planner.rs` **not touched**, matching
  the brief's "Interfaces" line. `git status` before freezing confirmed exactly these files.
- `docs/ROADMAP.md` §2 rule 10 respected: no changes to `game/engine.rs`, any existing
  `cgauto/submissions/*` file, or `rust/src/botmain/motion.rs`.
- No games played against the real API, nothing submitted to the arena — the Scale-probe smoke
  test used synthetic stdin/stdout wire input only (no `collect_debug_games.py`, no network),
  consistent with rule 7 (play-API throttle discipline) and the builder role's scope.

## 7. Next steps

Per `task-4-brief.md` Step 7: dispatch a **gatekeeper** for the Scale probe
(`data/candidates/v1.34.0-factory/v1.34.0-factory.scale-debug-probe.min.rs`, DEBUG=true,
GE_META=Scale, compile-checked, smoke-tested — no crash across 145 synthetic turns, phase flips
Hoard→Factory exactly at t=140) — `collect_debug_games.py <probe> boss 8` + field games per the
gatekeeper brief, checking the brief's Step 7 invariants: **PLANT count t150+ ≥25 per game**
(count in raws), **wood ≥60 in ≥4/8 boss games**, **t300 delta ≥ −8**. This gate can FAIL without
blocking future tasks (bands iterate) per the brief. Watch in particular whether farm_cap=20
actually gets *used*: it only helps if the Scale ladder's hands (wallet funded during Hoard) can
plant enough bananas to approach 20 slots before the game ends; if the ladder under-trains (e.g.
iron-poor maps stalling slot 2's `need_iron` gate), the bigger cap is a never-reached ceiling and
the next lever is the plant *rate*, not the cap.

## Gatekeeper verdict (Scale meta, B2+B3)

**Role:** combined GATEKEEPER for Task 3 (B2/hoard) + Task 4 (B3/factory), per the dispatching
agent's refined 6-readout brief (supersedes the separate Step-7 invariants written into
`task-3-brief.md`/`task-4-brief.md` at authoring time — this run is the actual first empirical
test of the two tasks together). Gatekeeper never submits to the arena; nothing below touched
`cgauto/api_submit.py` or the arena.

**Probe build — from the CURRENT tree (HEAD `1ba52a3`, i.e. including the `plan_with_meta`
test-seam commit, which is inert: it only factors `plan()` into `plan_impl` + a new unused-in-
production `pub fn plan_with_meta`, calling `plan_impl(state, my, super::GE_META)` exactly as
before — verified by re-reading the commit's diff before building):
```
cd rust && sed -i 's/Meta::Tempo;/Meta::Scale;/' src/botmain.rs   # (GE_META line only)
uv run --no-sync python tools/bundle.py       # 63773 chars
git checkout -- src/botmain.rs                # tree restored + verified clean/Tempo immediately
sed 's/DEBUG: bool = false;/true;/' bundled.rs > s.rs
uv run --no-sync python tools/minify.py s.rs s.min.rs   # 63772 -> 41763 chars
rustc --edition 2021 -O s.min.rs -o ccbin     # exit 0
```
Verified: `grep -c Meta::Scale s.min.rs` = 4; `grep DEBUG: bool = true` present. Probe kept in the
session scratchpad only (not frozen into the repo — ephemeral gatekeeper artifact, per role).
Cross-check: diffed the probe's Hoard-band logic against the builder's ALREADY-FROZEN
`v1.34.0-factory.scale-debug-probe.min.rs` (41,570 B; the 193-byte difference is exactly the
`plan_with_meta` seam) — **byte-identical band structure** (`62 * BAND`, `fund_hi` 45/44,
`want_chopper = false`), so every finding below is a property of the already-committed Task 3/4
source, not an artifact of this session's rebuild.

**Games played (all 12 completed the full 300 turns; zero HTTP 422s; zero crashes):**
- Boss ×8: `data/boss5_games/boss/game_895365{179,211,251,341,407,482,556,593}.{map,log,raw}`
- Field ×2 mikdiet (6480914): `data/boss5_games/6480914/game_895366{781,840}.*`
- Field ×2 plcc (6480966): `data/boss5_games/6480966/game_895366{890,943}.*`

### Readout 1 — phase schedule: HOLDS (8/8)
Every boss raw: last `@TFFARM ... phase=Hoard` sample at t=135, first `phase=Factory` sample at
t=140 (telemetry every 5 turns) — the T_SWITCH=140 boundary is exact in all 8 games.

### Readout 2 — hoard discipline (our wood at t≈150 ≤ 6, from .log): HOLDS, but vacuously (8/8)
All 8 games: wood@t150 = **0** (179:0, 211:0, 251:0, 341:0, 407:0, 482:0, 556:0, 593:0) — trivially
≤6. Not a meaningful pass: wood is 0 because nothing is EVER felled the entire game (readout 6),
not because Hoard is cleanly banking a wallet while suppressing production fells.

### Readout 3 — hands ladder: **FAILS** (5/8 < 6/8 bar)
`n` reaches 3 by t45 in only **5/8** games (179, 211, 251, 341, 482); the other 3 (407, 556, 593)
never get past n=2 for the entire game. Per-game n-schedule (first t each value of n is seen):
all 8 games: n=1→t5, n=2→t15 (SCALE_MIN_TURN[0]=10 gate). The 5 that progress: n=2→3→t45
(SCALE_MIN_TURN[1]=40 gate). **Max n reached, across all 8 games and the ENTIRE 300-turn duration
(not just by t140) = 3, in every single game.** The ladder's slot-2 hand — the ONLY chop-capable
unit the Scale meta ever specifies (`(2,2,0,2)`, gated `t≥110`) — never trains in any of the 8
games.

### Readout 4 — wallet (lemon ≥3 @ t≈100): diagnostic, holds directionally (7/8)
179:5, 211:4, 251:5, 341:3, 407:8, 482:13, 556:7, 593:2 → 7/8 ≥3 (only 593 misses, at 2).

### Readout 5 — factory output: diagnostic, **wood gain fails outright, farm-count is misleading**
Wood gain t150→300: **0 in all 8/8 games** (bar was ≥4/8 games ≥40 gain — off by the entire
margin, not close). `@TFFARM farm=` max at t150+: 179:6, 211:8, 251:10, 341:10, 407:11, 482:9,
556:11, 593:11 → 7/8 ≥8. This looks encouraging in isolation but is a trap: the farm regrows after
t140 only because Factory removes the Hoard-only wallet band (freeing the printer/plant path to
finally win a band contest) — trees accumulate because **nobody can ever chop them**, not because
the factory loop (plant→fell→bank) is running. Rising farm count + flat-zero wood is the signature
of an unharvested garden, not a production ramp.

### Readout 6 — overall: **FAILS catastrophically** (gating)
- Boss avg final wood = **0.0** (need ≥55 — fails by the entire bar). **All 8/8 games** finish at
  wood=0 (need: no game <25 — this is not a single outlier, it is universal). Boss score
  (us−opp) at t300: 179:−260, 211:−169, 251:−188, 341:−158, 407:−248, 482:−386, 556:−170,
  593:−137 (opponent final wood 26-88, avg 45.8 — `ramp.py`: t75 delta −4.2, t150 −12.1, t225
  −22.6, t300 −45.8, "late gain us +0.0 vs opp +23.1").
- Field: **4/4 losses**, every one worse than −150: mikdiet game1 56−291=**−235**, mikdiet game2
  29−461=**−432**; plcc game1 63−481=**−418**, plcc game2 29−505=**−476** (avg **−390**). Field
  wood: 0 for us in all 4 games too (opp 64, 106, 119, 124).

### Root cause (verified by reading the CURRENT `rust/src/botmain/planner.rs` directly)
The Hoard "wallet-building" band (`candidates()`, ~line 207-212: `value: 62 * BAND - eta(...)`,
fires for ANY reachable ripe fruit of ANY type, gated only on `plan.phase == Phase::Hoard`)
**unconditionally outranks** the iron-funding candidate a few lines below it (~line 213-232:
`value: fund_hi * BAND`, and under `Meta::Scale`, `want_chopper` is forced `false` at
`tactics.rs:132`, so `fund_hi = 45` always — never even the 60 "existential" tier). Since
62 > 50 (printer) > 45 (iron fund) > 42/40 (starter chop-help), and a ripe fruit tree is reachable
almost every turn on a real map, **no unit ever mines iron during Hoard.** The ladder's one
chop-capable slot (`(2,2,0,2)`, `cost[IRON] = n + chop² = 3 + 4 = 7` once n=3) can only ever be
paid from the map's *starting* iron endowment, because iron income is permanently zero — that
starting stock (2-7 across these 8 maps, e.g. game179's inventory trace: iron 5→2 by t45, then
frozen at 2 through t300) never reaches 7 in any sampled game, so **the chopper never trains, in
any of the 8 games.** With zero chop-capable units for the entire game (the starter's own
chop-help band, 40/42, is dominated by 62 the same way), wood production is deterministically
**zero for the full 300 turns, in both Hoard and Factory** — Task 4's `farm_cap` 12→20 and
reopened bands are correctly wired (readout 1 proves the phase flip; readout 5's farm-regrowth
proves band 62's removal reopens the printer path) but are moot, because the bottleneck was never
farm capacity — it's the chopper that never exists. In the 3 games that stall at n=2 (407, 556,
593), the identical missing-income problem bites one rung earlier: starting IRON below 2 blocks
even the ladder's SECOND hand (`cost[IRON]=2` at slot 1).
This is exactly the risk Task 3's own review flagged and left open (`progress.md`: "Gatekeeper
watch: iron cost on feeder slots (nobody mines it)") — it is not a corner case; it reproduced in
**12/12 games (100%)**, boss and field alike.

### Verdict: **FAIL**
Readouts 3 and 6 both fail on their own (gating); readout 1 holds; readout 2 holds only
vacuously. This is a logic defect in Task 3's Hoard wallet band (a priority-ordering bug), not a
tuning-margin miss — it wastes the entire game on every map sampled and must block Task 5 (B4
arena trial) until fixed. No crashes; no HTTP 422s; probe compiled clean both copies.

### Single most actionable observation
The Hoard wallet-building band's value (62) must not be allowed to outrank the iron-funding path
whenever a chop-capable troll is needed and iron is short — e.g. skip pushing the value-62
candidate for a troll while `plan.need_iron` is true (or give iron-mining its own unconditional
Hoard band above 62, or lower 62 below the funding tier). Until someone can mine iron during
Hoard, the ladder's only chopper slot is permanently unreachable on any map without a ≥7 starting
iron endowment, and the Scale meta banks exactly 0 wood, forever — Task 4's Factory-phase work is
sound but sits entirely downstream of a chopper that never gets born.

## Gatekeeper verdict #2 (Scale meta, post-B2.1)

**Role:** GATEKEEPER only (never submits to the arena; nothing below touched `cgauto/api_submit.py`
or the arena). Re-running the same 6-readout gate against `e09ac48` ("fix(b2.1): hoard iron band
64/63 + early iron target"), the fix written directly in response to verdict #1's root cause
(the Hoard wallet band, 62×BAND, unconditionally outranked iron-funding at 45×BAND, so nobody ever
mined and the ladder's chopper never trained — wood 0 in 12/12 games). HEAD at run time: `e09ac48`
(tip of `session-2026-07-01`; tree confirmed clean before and after the probe build).

**Probe build** (from the CURRENT tree, i.e. including `e09ac48`):
```
cd rust
sed -i 's/const GE_META: tactics::Meta = tactics::Meta::Tempo;/const GE_META: tactics::Meta = tactics::Meta::Scale;/' src/botmain.rs
uv run --no-sync python tools/bundle.py        # 64830 chars
git checkout -- src/botmain.rs                 # tree restored; verified clean + Tempo immediately
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' target/refactor/bundled.rs > s.rs
uv run --no-sync python tools/minify.py s.rs s.min.rs   # 64829 -> 41875 chars
cp s.min.rs cc.rs && rustc --edition 2021 -O cc.rs -o ccbin   # exit 0, COMPILE-OK
```
Verified: full `s.rs` contains `GE_META: tactics::Meta = tactics::Meta::Scale;` and
`DEBUG: bool = true` (both grep-confirmed, 1 hit each); minified `s.min.rs` contains 3×
`Meta::Scale` and `DEBUG: bool = true`. Probe kept in the session scratchpad only (ephemeral
gatekeeper artifact, per role) — not frozen into the repo.

**Games played (all 12 completed the full 300 turns; zero HTTP 422s; zero crashes):**
- Boss ×8: `data/boss5_games/boss/game_895368{157,180,198,221,238,266,280,299}.{map,log,raw}`
- Field ×2 mikdiet (6480914): `data/boss5_games/6480914/game_895368{323,339}.*`
- Field ×2 plcc (6480966): `data/boss5_games/6480966/game_895368{358,370}.*`

### Readout 1 — phase schedule: HOLDS (8/8)
Every boss raw: last `@TFFARM ... phase=Hoard` sample at t=135, first `phase=Factory` sample at
t=140 — the T_SWITCH=140 boundary is exact in all 8 games, identical to verdict #1 (this part of
B2/B3 was never in question).

### Readout 2 — hoard discipline (our wood at t≈150 ≤ 6, from .log): HOLDS, still mostly vacuous (8/8)
All 8 games: wood@t150 = **0** (157:0, 180:0, 198:0, 221:0, 238:0, 266:0, 280:0, 299:0) — trivially
≤6. Less vacuous than verdict #1 though: this time **1/8 (266)** goes on to actually bank wood after
t150 (34 by t300, see readout 5) — the first real (non-hypothetical) instance of the "hoard now,
factory produces after t150" story the phase design intends, even though the other 7/8 still bank
nothing for the entire game.

### Readout 3 — hands ladder: **FAILS** (5/8 < 6/8 bar; 1/8 ≪ 4/8 bar)
Per-game first-t each value of `n` is seen (all 8 games: n=1→t5, n=2→t15, the `SCALE_MIN_TURN[0]=10`
gate):
| game | n ladder (first-t) | max n | n≥3 by t140 | n==4 by t160 |
|---|---|---|---|---|
| 157 | 1@5, 2@15, 3@45 | 3 | YES (t45) | NO |
| 180 | 1@5, 2@15 | **2** | NO | NO |
| 198 | 1@5, 2@15 | **2** | NO | NO |
| 221 | 1@5, 2@15, 3@95 | 3 | YES (t95) | NO |
| 238 | 1@5, 2@15, 3@45 | 3 | YES (t45) | NO |
| 266 | 1@5, 2@15, 3@85, 4@145 | **4** | YES (t85) | YES (t145) |
| 280 | 1@5, 2@15, 3@45 | 3 | YES (t45) | NO |
| 299 | 1@5, 2@15 | **2** | NO | NO |

n≥3 by t140: **5/8** (need ≥6) → miss by one. n==4 (the chopper slot) by t160: **1/8** (need ≥4) →
miss by three-quarters of the bar. **Across the full 300-turn game (not just by t160), the chopper
trains in exactly 1/8 games (266)** — the other 7/8 never train it at all, for the entire match.

### Readout 4 — wallet (diagnostic): iron mixed (4/8), lemon holds directionally (6/8)
| game | iron@t110 | iron first≥7 | lemon@t100 |
|---|---|---|---|
| 157 | 1 MISS | t138 | 4 OK |
| 180 | 9 OK | t1 (map start) | 2 MISS |
| 198 | 9 OK | t1 (map start) | 9 OK |
| 221 | 4 MISS | t126 | 0 MISS |
| 238 | 7 OK | t1 (map start≈10, mines down to plateau 7) | 8 OK |
| 266 | 5 MISS | t1 (map start, dips then recovers) | 8 OK |
| 280 | 0 MISS | **never** (plateaus at 3-4 all game) | 16 OK |
| 299 | 8 OK | t1 (map start) | 7 OK |

iron≥7 by t110: **4/8** (need ≥5, diagnostic). lemon≥3@t100: **6/8** (diagnostic). Important
qualifier found by tracing full iron histories (not just the t110 snapshot): in the 5 games that
start with iron ≥7 already on the map (180, 198, 238, 266, 299), the bar is met by map luck, not by
the fix. In the 3 low-endowment games (157, 221, 280), the fix **does** now cause real mining
(iron rises over time — e.g. 157: 1→2→7 between t100-140; 221: 4→6→7 between t100-140 — this did
not happen at all pre-fix, where iron only ever fell or sat flat). But 280's iron mining stalls at
3-4 and never reaches 7 for the rest of the 300-turn game, so even where the fix engages, it does
not always finish the job in time.

### Readout 5 — factory output (the decider): **FAILS on every sub-bar**
| game | wood@150 | wood@300 | gain | opp final wood |
|---|---|---|---|---|
| 157 | 0 | 0 | 0 | 38 |
| 180 | 0 | 0 | 0 | 36 |
| 198 | 0 | 0 | 0 | 34 |
| 221 | 0 | 0 | 0 | 46 |
| 238 | 0 | 0 | 0 | 74 |
| 266 | 0 | **34** | **34** | 52 |
| 280 | 0 | 0 | 0 | 34 |
| 299 | 0 | 0 | 0 | 38 |

gain(t150→300)≥40: **0/8** (need ≥4 — even the one game with any production, 266, gains only 34,
short of the 40 bar). Avg final wood = **4.2** (need ≥55 — off by the entire bar). Games with final
wood <25: **7/8** (need 0 — this is not a single outlier, it is 7 of 8 maps). Opp avg final wood =
**44.0**. This is a small, real improvement over verdict #1 (which was 0/8 wood, avg 0.0) but is
still catastrophically short of a passing factory economy.

### Readout 6 — field: **FAILS** (3/3 losses worse than −150; win rate 1/4)
| game | opp | result | wood | scores | delta |
|---|---|---|---|---|---|
| 895368323 | mikdiet | **WIN** | 49–17 | [234, 113] | **+121** |
| 895368339 | mikdiet | LOSS | 0–70 | [35, 302] | **−267** (violation) |
| 895368358 | plcc | LOSS | 0–91 | [75, 376] | **−301** (violation) |
| 895368370 | plcc | LOSS | 0–93 | [38, 390] | **−352** (violation, worst) |

All 3 losses exceed the −150 bar (worst = **−352**); only the 1 win is clean. This is a substantial
improvement over verdict #1 (4/4 losses, avg −390, all wood 0) — one game now actually wins — but
the gate still fails outright since any loss worse than −150 fails it, and 3/3 sampled losses do.

### Root cause (verified by reading the CURRENT `rust/src/botmain/{tactics,planner}.rs` directly)
`e09ac48` is a correct, working fix for exactly what it targeted: `tactics.rs:142`
(`let need_iron = have_iron && inv[IRON] < 7;`, widened from "only once slot 2" to "any time
short") plus `planner.rs:226-239` (the Mine/MoveTo-to-iron candidates get value 64/63 during Hoard,
**now correctly outranking** the generic wallet band at `planner.rs:207-211`
(`value: 62 * BAND - eta(...)`)). Confirmed empirically: in the 3 low-iron-endowment games
(157, 221, 280), iron now visibly **rises** over time via real mining — this never happened in
verdict #1's 8 games (iron only ever fell or sat flat, "frozen at 2 through t300").

But the slot-2 chopper spec `SCALE_LADDER[2] = (2,2,0,2)` (`tactics.rs:128`) costs **four** resources
simultaneously via `training_cost` (`state.rs:142-149`): at n=3, cost = `PLUM:7, LEMON:7, APPLE:3,
IRON:7`. Only IRON got the priority-bump treatment. The parallel per-fruit-type targeting candidate
for PLUM/LEMON/APPLE — `need_fund[t]` (`tactics.rs:143`), pushed at `planner.rs:241-248` with
`value: fund_lo * BAND` where `fund_lo` is **always 44** under Scale (`planner.rs:219`:
`if plan.want_chopper { (60,58) } else { (45,44) }`, and Scale hardcodes `want_chopper = false` at
`tactics.rs:132`, so the `58` branch is dead) — was **not** bumped. 44 < 62, so during Hoard a
troll still just walks to "whatever ripe fruit is nearest" (band 62) rather than specifically the
fruit type the ladder is short on. This is **the same bug class `e09ac48` just fixed for iron**,
now gating on PLUM/LEMON/APPLE instead:
- **3/8 games (180, 198, 299) never even clear slot 1** (n=2→3, cost 3 each): 180's PLUM is stuck at
  **1** for the entire 300 turns (verified full trace: t100/150/200/250/299 all read PLUM=1); 198's
  PLUM is likewise stuck at **1** the whole game; 299's APPLE is stuck at **1** the whole game — in
  all 3 cases every OTHER resource is abundant (e.g. 198: LEMON=9, APPLE=5, IRON=9 the whole game),
  it is specifically one starved fruit type, forever, despite 150+ idle turns after t150 to fix it.
- **4/8 games clear slot 1 (n=3) but never clear slot 2** (cost 7 on 3 of 4 resources): 157's PLUM
  sticks at 5 (needs 7), 221's LEMON sticks at 5 (needs 7), 238's PLUM sticks at 3 (needs 7), 280's
  IRON sticks at 3-4 (needs 7 — this is the ONE case where `e09ac48`'s own target resource is still
  short at game end, i.e. the fix helps but does not always finish within 300 turns).
- **1/8 (266) is the only game where all four resources cleared slot 2's bar together** — traced
  turn-by-turn: at t140 (Factory just started) PLUM=6, LEMON=8, APPLE=11, IRON=7; PLUM ticks 6→7 at
  t141 (the last of the four to arrive); training fires at t142 (a 6th troll, id 5, appears; every
  inventory drops by exactly cost `(7,7,3,7)` in that single turn). This is the only boss game with
  any wood (34 final).

**Cross-validated outside boss:** the field win (mikdiet, 895368323) reached n=4 at **t=115** (the
earliest chopper of any of the 12 games sampled) and won 49–17 / scores +121. All 3 field losses
stalled at n=2 (both plcc games, immediately after `SCALE_MIN_TURN[0]`, never progressing at all)
or n=3 (the other mikdiet game, stuck from t150 onward) and scored 0 wood. **Across all 12 games
sampled this run, the chopper trained in exactly 2 (266 boss, 895368323 field) — and those are the
only 2 games with any wood production or a win.** The other 10/12 (83%) reproduce the pre-fix
failure mode exactly, just gated one resource-type later in the dependency chain than before.

### Verdict: **FAIL**
Readouts 3, 5, and 6 all fail on their own (gating); readout 1 holds; readout 2 holds only
vacuously (7/8) / weakly (1/8 — 266). `e09ac48` measurably works (iron now actively accumulates via
real mining where it previously never did, and one game each in the boss and field samples now
trains the chopper and produces wood/wins where verdict #1 had zero), but it is a partial fix: it
special-cased iron alone inside a 4-resource simultaneous-funding requirement, and 10/12 games this
run stall on one of the THREE resources (PLUM/LEMON/APPLE) that did not get the same treatment. No
crashes; no HTTP 422s; probe compiled clean (full and minified).

### Single most actionable observation
Generalize `e09ac48`'s fix from iron to all of `need_fund[0..3]` (PLUM/LEMON/APPLE): the
`need_fund`-driven candidates at `planner.rs:241-248` (currently pushed at `fund_lo=44*BAND`,
constant under Scale since `want_chopper` is hardcoded false) must outrank the generic Hoard
wallet band (`62*BAND`, `planner.rs:207-211`) whenever the specific fruit type is the ladder's
current bottleneck — the same priority-bump `e09ac48` already gave `need_iron`'s Mine/MoveTo
candidates (64/63, both now legitimately above 62). Right now 10 of the 12 games sampled (83%)
stall for the ENTIRE remaining game on exactly one stuck PLUM/LEMON/APPLE/IRON count that never
climbs past whatever the generic "walk to nearest ripe fruit" behavior happens to supply — 3/8
games stuck below the slot-1 bar (cost 3) and 5/8 (4 boss + the mikdiet field loss) stuck below the
slot-2 bar (cost 7 on 3 of 4 resources). This is not a new bug — it is the identical band-62-vs-
targeted-funding priority bug `e09ac48` fixed, recurring at the three resource types that fix did
not touch. Until `need_fund`'s candidates get the same priority bump, the Scale ladder will keep
training its chopper in roughly 1 game out of 6 (2/12 here), gated by whichever single fruit type a
given map happens to be locally poor in near the wallet-gathering path.

## Gatekeeper verdict #3 (Scale meta, post-B2.2)

**Role:** GATEKEEPER only (never submits to the arena; nothing below touched `cgauto/api_submit.py`
or the arena). Re-running the same style of gate against `b14ebc7` ("fix(b2.2): hoard deficit-fruit
band 63 — targeted funding outranks the generic wallet"), the fix written directly in response to
verdict #2's root cause (iron got the priority bump in `e09ac48`/B2.1, but PLUM/LEMON/APPLE funding
was still dominated by the generic 62-band wallet candidate, so 10/12 games stalled on one of those
three types). HEAD at run time: `b14ebc7` (tip of `session-2026-07-01`; tree confirmed clean before
and after the probe build).

**Probe build** (from the CURRENT tree, i.e. including `b14ebc7`), exactly mirroring verdict #2's
recipe:
```
cd rust
sed -i 's/const GE_META: tactics::Meta = tactics::Meta::Tempo;/const GE_META: tactics::Meta = tactics::Meta::Scale;/' src/botmain.rs
uv run --no-sync python tools/bundle.py        # 65450 chars
git checkout -- src/botmain.rs                 # tree restored; verified clean + Tempo immediately
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' target/refactor/bundled.rs > s.rs
uv run --no-sync python tools/minify.py s.rs s.min.rs   # 65449 -> 41962 chars
cp s.min.rs dotfree.rs && rustc --edition 2021 -O dotfree.rs -o ccbin   # exit 0, COMPILE-OK (both full + minified copies)
```
Verified: full `s.rs` contains `Meta::Scale` (4 hits), `const DEBUG: bool = true` (1 hit),
`fruit_band` (2 hits — the B2.2 fix's new binding + its use site); minified copy contains
`Meta::Scale` (3 hits), `DEBUG: bool = true` (1 hit), `fruit_band` (2 hits). `rust/src/botmain.rs`
confirmed back to `Meta::Tempo` and `git status --short` clean in `rust/` immediately after the
bundle step, before any games were played. Probe kept in the session scratchpad only (ephemeral
gatekeeper artifact, per role) — not frozen into the repo.

**Games played (all completed the full 300 turns; zero crashes):**
- Boss ×8: `data/boss5_games/boss/game_895373{184,212,239,258,279,291,303,319}.{map,log,raw}`
- Field vs mikdiet (6480914) ×3: `data/boss5_games/6480914/game_8953{73543,74625,74658}.*`
  (requested ×2; got 1/2 on the first pass — the 2nd call hit **HTTP 422**; per instructions,
  waited 15 min once, then retried the full ×2 batch and got both cleanly, for 3 total)
- Field vs plcc (6480966) ×3: `data/boss5_games/6480966/game_8953{73567,74707,74740}.*`
  (same pattern — 1st call hit **HTTP 422** on the 1st sub-game, 2nd sub-game succeeded; the
  post-wait retry then landed both, for 3 total)
- **One HTTP 422 retry cycle used, exactly per the brief's "on 422: wait 15 min once" rule** — no
  second wait, no further retries; all numbers below use every game that came back (14 total: 8
  boss + 6 field), not just the minimum requested 4 field games.

### Readout 1 — phase flip t=140: **HOLDS (8/8)**
Every boss raw: last `@TFFARM ... phase=Hoard` sample at t=135, first `phase=Factory` sample at
t=140, in all 8 games — identical to verdicts #1/#2 (this part of B1-B3 has never regressed).

### Readout 2 — HANDS (the fix's direct target): **FAILS** (n=4 sub-bar misses by the entire bar)
First-t per value of `n`, per boss game (all 8: n=1→t5, n=2→t15, the fixed early gates):

| game | n=3 first-t | max n (whole 300-turn game) | n≥3 by t140 | n=4 by t≈160 |
|---|---|---|---|---|
| 184 | t45 | 3 | YES | NO (never) |
| 212 | t45 | 3 | YES | NO (never) |
| 239 | t115 | 3 | YES | NO (never) |
| 258 | — (stuck at n=2) | **2** | NO | NO (never) |
| 279 | t55 | 3 | YES | NO (never) |
| 291 | t65 | 3 | YES | NO (never) |
| 303 | t45 | 3 | YES | NO (never) |
| 319 | t45 | 3 | YES | NO (never) |

n≥3 by t140: **7/8** (need ≥6/8 — holds). n=4 by t≈160: **0/8** (need ≥4/8 — fails by the entire
bar). More striking than "by t160": **across the full 300-turn duration, n never reaches 4 in any
of the 8 boss games** — the ladder's only chop-capable slot (the actual fix target) trained in
zero boss games this run, down from verdict #2's 1/8 (266). Cross-checked against field (below):
n=4 fires in exactly **1 of 6** field games (plcc 895374707, at t=150 — 10 turns after the Factory
switch, the wallet finished just barely too late to matter under Hoard's own priority rules); the
other 5/6 field games max out at n=3, same signature as boss. **Aggregate across all 14 games
sampled this run: chopper trains in 1/14 (7%)** — worse than verdict #2's 2/12 (17%), and materially
indistinguishable from verdict #1's 0/12 in practical terms (still essentially "never").

### Readout 3 — FACTORY OUTPUT (the decider): **FAILS on every sub-bar, reverts to verdict #1's zero**
| game | wood@150 | wood@300 (ours) | gain(150→300) | opp final wood | boss score (us−opp) |
|---|---|---|---|---|---|
| 184 | 0 | 0 | 0 | 38 | 27−203 = **−176** |
| 212 | 0 | 0 | 0 | 32 | 25−187 = **−162** |
| 239 | 0 | 0 | 0 | 63 | 21−321 = **−300** |
| 258 | 0 | 0 | 0 | 26 | 33−150 = **−117** |
| 279 | 0 | 0 | 0 | 46 | 45−217 = **−172** |
| 291 | 0 | 0 | 0 | 56 | 22−243 = **−221** |
| 303 | 0 | 0 | 0 | 40 | 28−227 = **−199** |
| 319 | 0 | 0 | 0 | 58 | 49−270 = **−221** |

gain(t150→300)≥40: **0/8** (need ≥4/8). Avg final wood = **0.0** (need ≥55 — off by the entire
bar). Games with final wood <25: **8/8** (need 0 — universal, not an outlier). Opp avg final wood =
**44.9**. Boss win rate **0/8**, avg score delta **−196**. This is **not** an improvement over
verdict #2 (avg wood 4.2, 1/8 games with any production) — it is a **full reversion to verdict #1's
0/8-wood, 0.0-avg total failure**, despite B2.2 being a targeted, verified-correct fix for exactly
the bug verdict #2 found.

### Readout 4 — WALLET diagnostics (not gating): iron regresses to worst-yet, lemon/plum mixed
Snapshot values (not "ever reached", per verdict #2's own methodology) — `iron@t110`, `lemon@t100`,
`plum@t110`:

| game | iron@110 | lemon@100 | plum@110 |
|---|---|---|---|
| 184 | 0 MISS | 0 MISS | 9 OK |
| 212 | 5 MISS | 1 MISS | 11 OK |
| 239 | 6 MISS | 13 OK | 12 OK |
| 258 | 1 MISS | 13 OK | 1 MISS |
| 279 | 5 MISS | 3 OK | 14 OK |
| 291 | 6 MISS | 1 MISS | 11 OK |
| 303 | 5 MISS | 6 OK | 4 MISS |
| 319 | 4 MISS | 2 MISS | 13 OK |

iron≥7@t110: **0/8** (verdict #2 was 4/8 — this run is worse on the exact resource B2.1 targeted).
lemon≥3@t100: **4/8**. plum≥7@t110: **6/8**. Unlike verdict #2 (where the short resource varied
game-to-game and was usually a single type), **iron is short in 8/8 games this run** — a much more
uniform failure than either prior verdict saw for any single resource. See Root Cause: this lines up
exactly with a code-level mechanism, not just map luck.

### Readout 5 — Hoard discipline (wood ≤6 @t150): **HOLDS, still fully vacuous (8/8)**
All 8 games: wood@t150 = 0 (trivially ≤6). As in both prior verdicts, this passes only because
nothing is ever felled at all (readout 3), not because Hoard is banking cleanly while suppressing a
real production stream.

### Readout 6 — Field: **FAILS** (6/6 losses worse than −150, not just the minimum-required 4)
| game | opp | result | wood (us-opp) | scores | delta |
|---|---|---|---|---|---|
| 895373543 | mikdiet | LOSS | 0–116 | [16, 483] | **−467** |
| 895374625 | mikdiet | LOSS | 0–80 | [20, 366] | **−346** |
| 895374658 | mikdiet | LOSS | 0–90 | [57, 441] | **−384** |
| 895373567 | plcc | LOSS | 0–107 | [30, 433] | **−403** |
| 895374707 | plcc | LOSS | 50–102 | [226, 416] | **−190** |
| 895374740 | plcc | LOSS | 0–130 | [30, 527] | **−497** |

**0/6 wins, 6/6 losses worse than −150** (best case −190, worst −497, avg **−381**). 895374707 is
the one bright spot in the whole 14-game sample: it is both the only field game with any wood at
all (50, from the one n=4 chopper training at t=150) and the smallest-margin loss (−190) — still a
gate violation, but directionally consistent with "train the chopper → produce wood → lose by
less," which is the mechanism the whole B2/B3 arc is betting on. It just doesn't fire reliably.

### Root cause (verified by reading the CURRENT `rust/src/botmain/{tactics,planner}.rs` directly)
`b14ebc7` is exactly what it claims to be: a correct, narrowly-scoped fix that makes the deficit-
fruit `MoveTo` candidate (`planner.rs`, `let fruit_band = if plan.phase == Phase::Hoard { 63 } else
{ fund_lo };`) outrank the generic wallet band (62) during Hoard, closing the specific gap verdict
#2 found. Inspecting it next to the iron fix it was modeled on (`e09ac48`, `hoard_iron` → 64/63)
surfaces the thing neither fix's own author flagged: **the two now share the exact same numeric
band, 63, for their `MoveTo` candidates.** Iron's `MoveTo` and the new fruit-deficit `MoveTo` are
no longer in a deliberate priority order — they compete purely on `eta` (travel distance), because
`value = 63 * BAND - eta(...)` for both. Since the ladder's slot-2 hand needs **all four** resources
funded simultaneously (`training_cost(3, (2,2,0,2))` = `PLUM:7, LEMON:7, APPLE:3, IRON:7`, unchanged
since verdict #2), and `need_iron`/`need_fund[t]` are frequently true at the same time for the same
troll (verified directly in the traces above — e.g. game 184 has iron and lemon both short for most
of the game simultaneously), this is not a hypothetical collision: on every turn where a troll can
see both an iron cell and a deficit fruit tree, whichever is physically closer wins, regardless of
which resource is scarcer. Iron cells are plausibly sparser/farther than fruit trees on typical maps
(there are usually many trees but few iron deposits), which would explain why iron — the one
resource with **no fruit-harvest fallback**, per B2.1's own comment ("iron is scarce and un-
substitutable") — is now short in 8/8 games, the most uniform failure of any resource across all
three verdicts. **A second, compounding factor**: both the generic wallet band (62) and the fixed
funding bands (63/64) are gated `plan.phase == Phase::Hoard` only — at t=140 (Factory) they all
evaporate simultaneously, dropping funding priority back to `fund_lo`=44 (`want_chopper` is
hardcoded `false` under Scale, so the 58 tier is dead), which sits below Printer (50/48). Game
895374707's chopper trained at **t=150, ten turns after** this cliff — meaning the wallet was
*already essentially complete* when Hoard ended, and finished only by leftover momentum; every
other game's wallet was still missing at least one resource (usually iron) at t=140 and, per this
mechanism, was then structurally abandoned in favor of Printer work for the remaining 160 turns,
which matches the observed "stuck forever past t150" pattern in readout 4 exactly.

### Verdict: **FAIL**
Readouts 2, 3, and 6 all fail on their own (gating: PASS requires 1, 2, 3, 6); readout 1 holds;
readout 5 holds only vacuously. `b14ebc7` is a verified-correct, narrow fix for exactly the bug
verdict #2 diagnosed, but it does not move the needle empirically — this run is a full reversion to
verdict #1's total-failure state (0/8 boss wood, 0/8 boss wins, 6/6 field losses worse than −150),
worse on the chopper-training rate than verdict #2 (1/14 vs 2/12) and worse on iron specifically
(0/8 vs 4/8 games ≥7 by t110) — the exact resource the immediately-prior fix targeted. No crashes;
one HTTP 422 retry cycle used per the brief's rule, both batches succeeded on retry.

### Single most actionable observation
`e09ac48` (iron) and `b14ebc7` (fruit) independently picked the **same priority number, 63**, for
their `MoveTo` candidates, so a troll facing both an iron shortfall and a fruit shortfall at once —
which happens routinely, since the ladder's final hand needs all four resources at once — now
resolves the choice by raw travel distance instead of any deliberate ordering, and iron (previously
the sole occupant of that band, per verdict #2) is the apparent loser: it is short at t110 in 8/8
games this run, the most uniform single-resource failure across all three verdicts. The fix: give
iron's Hoard-phase `Mine`/`MoveTo` bands a value strictly above 63 (e.g. 65/64, preserving the
64-vs-63 Mine/MoveTo gap already used) so it keeps unconditional priority over fruit funding — iron
has no harvest alternative and B2.1's own comment already asserts it should never lose this race.
Second, independent lever worth testing regardless: the Hoard-only gating on all three funding
bands (62/63/64) creates a hard cliff at T_SWITCH=140 — a wallet that is one resource-tick away from
complete gets fully abandoned the instant Factory starts (game 895374707's t=150 chopper is the one
case that survived this cliff, by 10 turns of leftover momentum). Either push `T_SWITCH` a bit later,
or let the funding bands stay elevated for a short grace window past 140 until the ladder's last
hand actually trains, before conceding the priority to Printer work.

## Gatekeeper verdict #4 (Scale meta, post-B2.3)

**Role:** GATEKEEPER only (never submits to the arena; nothing below touched `cgauto/api_submit.py`
or the arena). Re-running the same style of gate against `0ecbc66` ("fix(b2.3): iron 65/64
unconditional + funding grace window past T_SWITCH (want_feeder-scoped) — gatekeeper #3 root
causes"), the fix written directly in response to verdict #3's two root causes: (a) **band
collision** — `e09ac48` (iron) and `b14ebc7` (fruit) both used band 63, so iron lost distance races
to fruit 8/8 games; fixed by bumping iron to 65/64, strictly above fruit's 63. (b) **T_SWITCH
cliff** — all funding bands were gated `phase == Phase::Hoard` only, so a nearly-complete wallet was
abandoned the instant Factory began; fixed by a `scale_funding = plan.phase != Phase::Tempo &&
plan.want_feeder` grace window that keeps funding elevated until the ladder actually finishes
(`want_feeder` self-extinguishes once `n` reaches 4), and is a no-op on the live Tempo path since
`phase_for(Tempo, _) == Phase::Tempo` always. HEAD at run time: `0ecbc66` (tip of
`session-2026-07-01`; tree confirmed clean before and after the probe build).

**Probe build** (from the CURRENT tree, i.e. including `0ecbc66`), exactly mirroring verdicts #2/#3's
recipe:
```
cd rust
sed -i 's/const GE_META: tactics::Meta = tactics::Meta::Tempo;/const GE_META: tactics::Meta = tactics::Meta::Scale;/' src/botmain.rs
uv run --no-sync python tools/bundle.py        # 66146 chars
git checkout -- src/botmain.rs                 # tree restored; verified clean + Tempo immediately
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' target/refactor/bundled.rs > v4_s.rs
uv run --no-sync python tools/minify.py v4_s.rs v4_s.min.rs   # 66145 -> 41978 chars
cp v4_s.rs v4cc.rs && rustc --edition 2021 -O v4cc.rs -o v4_full_bin      # exit 0, COMPILE-OK
cp v4_s.min.rs v4mcc.rs && rustc --edition 2021 -O v4mcc.rs -o v4_min_bin # exit 0, COMPILE-OK
```
Verified: full `v4_s.rs` contains `Meta::Scale` (4 hits), `const DEBUG: bool = true` (1 hit),
`scale_funding` (5 hits — the B2.3 fix's new binding, its 3 use sites, plus one mention in a
comment); minified `v4_s.min.rs` contains `Meta::Scale` (3 hits — comments stripped), `DEBUG: bool =
true` (1 hit), `scale_funding` (4 hits — code only). `rust/src/botmain.rs` confirmed back to
`Meta::Tempo` and `git status --short` clean in `rust/` immediately after the bundle step, before any
games were played. Probe kept in the session scratchpad only (ephemeral gatekeeper artifact, per
role) — not frozen into the repo.

**Games played (all 12 completed the full 300 turns; zero crashes; zero HTTP 422s — no retry needed):**
- Boss ×8: `data/boss5_games/boss/game_895375{939,969}.{map,log,raw}`,
  `game_895376{000,019,045,060,092,109}.{map,log,raw}`
- Field vs mikdiet (6480914) ×2: `data/boss5_games/6480914/game_895376{185,208}.*`
- Field vs plcc (6480966) ×2: `data/boss5_games/6480966/game_895376{230,247}.*`

### Readout 1 — phase flip t=140: **HOLDS (8/8)**
Every boss raw: last `@TFFARM ... phase=Hoard` sample at t=135, first `phase=Factory` sample at
t=140, in all 8 games — identical to every prior verdict (this part of B1-B3 has never regressed).

### Readout 2 — HANDS (the fix's direct target): **HOLDS for the first time in the whole B2 arc**
First-t per value of `n`, per boss game (all 8: n=1→t5, n=2→t15, unchanged early gates):

| game | n-ladder (first-t) | max n | n≥3 by t140 | n=4 EVER (whole game) |
|---|---|---|---|---|
| 895375939 | 1@5, 2@15, 3@45, 4@195 | 4 | YES (t45) | YES (t195) |
| 895375969 | 1@5, 2@15 | **2** | NO | NO (never) |
| 895376000 | 1@5, 2@15, 3@60, 4@160 | 4 | YES (t60) | YES (t160) |
| 895376019 | 1@5, 2@15, 3@70, 4@260 | 4 | YES (t70) | YES (t260) |
| 895376045 | 1@5, 2@15, 3@45, 4@180 | 4 | YES (t45) | YES (t180) |
| 895376060 | 1@5, 2@15, 3@65, 4@150 | 4 | YES (t65) | YES (t150) |
| 895376092 | 1@5, 2@15, 3@45, 4@235 | 4 | YES (t45) | YES (t235) |
| 895376109 | 1@5, 2@15, 3@45, 4@165 | 4 | YES (t45) | YES (t165) |

n≥3 by t140: **7/8** (need ≥6/8 — holds; same bar verdict #3 already met). n=4 EVER: **7/8** (need
≥5/8 — holds decisively; verdict #3 was **0/8**, verdict #2 was 1/8, verdict #1 was 0/8). This is the
first run across the entire B2/B2.1/B2.2/B2.3 arc where the ladder's only chop-capable hand reliably
trains. Mean first-t(n=4) across the 7 games that reach it ≈ **192** (range 150-260). The one holdout,
895375969, never progresses past n=2 for the entire 300-turn game (see Root cause).

### Readout 3 — FACTORY OUTPUT (the decider): **FAILS on every sub-bar**
| game | wood@150 | wood@300 (ours) | gain(150→300) | opp final wood | boss score (us−opp) |
|---|---|---|---|---|---|
| 895375939 | 0 | 30 | 30 | 48 | 127−229 = **−102** |
| 895375969 | 0 | 0 | 0 | 54 | 47−247 = **−200** |
| 895376000 | 0 | 32 | 32 | 43 | 143−217 = **−74** |
| 895376019 | 0 | 12 | 12 | 111 | 76−517 = **−441** |
| 895376045 | 0 | 30 | 30 | 75 | 139−301 = **−162** |
| 895376060 | 0 | 18 | 18 | 56 | 111−246 = **−135** |
| 895376092 | 0 | 16 | 16 | 44 | 71−237 = **−166** |
| 895376109 | 0 | 48 | 48 | 50 | 200−272 = **−72** |

gain(t150→300)≥40: **1/8** (895376109 only; need ≥4/8). Avg final wood = **23.2** (need ≥55 — real
production for the first time in the arc, but under half the bar). Games with final wood <25: **4/8**
(895375969=0, 895376019=12, 895376060=18, 895376092=16; need 0). Opp avg final wood = **60.1**. Boss
win rate **0/8**, avg score delta **−169.0** (an improvement over verdict #3's −196, but still a
comfortable Boss-5 win on every sampled map).

### Readout 4 — WALLET diagnostics (not gating): iron/apple usually funded by t140, plum/lemon usually not
Snapshot values at t≈140 (`@TFD`, nearest sample):

| game | plum@140 | lemon@140 | apple@140 | iron@140 |
|---|---|---|---|---|
| 895375939 | 12 OK | 3 MISS | 3 MISS | 3 MISS |
| 895375969 | 5 MISS | 1 MISS | 16 OK | 8 OK |
| 895376000 | 10 OK | 4 MISS | 12 OK | 7 OK |
| 895376019 | 3 MISS | 6 MISS | 28 OK | 7 OK |
| 895376045 | 3 MISS | 19 OK | 6 MISS | 7 OK |
| 895376060 | 6 MISS | 6 MISS | 28 OK | 7 OK |
| 895376092 | 2 MISS | 3 MISS | 9 OK | 3 MISS |
| 895376109 | 6 MISS | 4 MISS | 8 OK | 7 OK |

By t140, ≥7: iron **6/8**, plum **2/8**, lemon **1/8**, apple **6/8** (all diagnostic, not gating).
Iron (the B2.3 fix's own priority target) and apple are usually funded on time; plum and especially
lemon usually are not — but per readout 2 this no longer blocks the ladder outright, because
`scale_funding`'s grace window now lets funding keep working past t140 until whichever resource is
slowest finally arrives (median completion ≈ t192, well past the old t140 cliff).

### Readout 5 — Hoard discipline (wood ≤6 @t150): **HOLDS (8/8), less vacuous than prior verdicts**
All 8 games: wood@t150 = 0 (trivially ≤6). Still effectively vacuous for most games (the chopper
hasn't finished training by t150 in 6/8 of them — see readout 2), but no longer vacuous for the
*reason* verdicts #1-#3 saw (nothing ever felled all game) — this run's chopper does go on to fell
real wood in 7/8 games, just mostly after t150.

### Readout 6 — Field: **FAILS** (4/4 losses worse than −150)
| game | opp | result | wood (us-opp) | scores | delta | n=4 ever? |
|---|---|---|---|---|---|---|
| 895376185 | mikdiet | LOSS | 0–112 | [42, 522] | **−480** | NO (max n=3 @t185) |
| 895376208 | mikdiet | LOSS | 0–118 | [36, 494] | **−458** | NO (max n=3 @t50) |
| 895376230 | plcc | LOSS | 22–91 | [109, 372] | **−263** | YES (t165) |
| 895376247 | plcc | LOSS | 1–109 | [34, 444] | **−410** | NO (max n=3 @t70) |

**0/4 wins, 4/4 losses worse than −150** (best case −263, worst −480, avg **−403**). The one field
game where the ladder actually completes (895376230, n=4 at t165) is also the only field game with
non-trivial wood (22) and the smallest-margin loss (−263) — the same "train the chopper → produce
wood → lose by less" signature verdict #3 saw, but the ladder only ever completes in **1/4** field
games this run (worse than boss's 7/8) — real opponents apply enough denial/tempo pressure that the
funding grace window frequently never gets to finish at all within 300 turns.

### Root cause (verified by reading the CURRENT `rust/src/botmain/{tactics,planner}.rs` directly, plus telemetry)
`0ecbc66` is a correct, verified-working fix for both defects verdict #3 diagnosed: readout 2 — the
fix's direct target — now holds decisively (n=4 EVER 7/8, up from 0/8 in verdict #3), and boss score
delta improves (−169.0 vs −196). But fixing the training gate exposes the next bottleneck downstream,
now visible for the first time because the chopper finally exists to reveal it:
- **The ladder is fixed at 3 rungs and hard-capped at n=4 forever**: `let want_hand = n < 4 &&
  state.turn >= SCALE_MIN_TURN[slot];` (`tactics.rs:131`) against `const SCALE_LADDER: [(i32, i32,
  i32, i32); 3]` (`tactics.rs:128`) — there is no 4th rung. Confirmed empirically: `max_n` is exactly
  4 in every one of the 7 boss games that complete the ladder, and never exceeds 4 in any of the 12
  games sampled this run (boss or field). For the remainder of every game — up to 150 turns after the
  earliest observed completion (t150) — **at most one chop=2 troll exists**, while opponents keep
  growing: mikdiet's build strings train troll id 4 (5 total trolls), plcc's train up to troll id 7
  (8 total trolls), over the same 300 turns.
- **Even the earliest-training case underperforms the bar**: game 895376060 reaches n=4 at t150 (the
  earliest in this sample) yet only gains 18 wood over the full remaining 150 turns (0.12 wood/turn)
  — under half the ≥40 bar with the maximum possible production window. This means the shortfall is
  not purely "the chopper trains too late": a single chop=2 hand's ceiling throughput, even given the
  entire rest of the game, undershoots the bar on this run's maps.
- **The farm itself stays small the whole game**: `@TFFARM farm=` never exceeds 10 at any checkpoint
  in any of the 8 boss games (e.g. 895376019 peaks at farm=10 at t225), far under both the pre-Factory
  12-slot cap and B3's new 20-slot cap — so the bigger farm B3 built is not yet the constraint. Root
  cause: `scale_funding` (`planner.rs`, gated on `want_feeder`) keeps outranking Printer/plant work
  (50/48) for as long as the ladder is incomplete — up to t260 in the slowest boss game and for the
  *entire* game in 3/4 field games — so there are too few un-conscripted turns of plant/printer work
  before the ladder finishes to grow the farm in the first place; by the time funding relents, only a
  shrinking tail of the match remains to plant, mature, and fell.
- **The one boss game that never completes the ladder (895375969) has a distinct, map-side cause**:
  traced the full `@TFD` history — LEMON is frozen at exactly **1** from t50 through t299 (needs 3 for
  even slot 1), while PLUM(5), APPLE(9→34), and IRON(8) are all healthy the entire game. This is a "no
  reachable lemon supply" dead end on this specific map, not a priority-band bug — outside what any
  Hoard-phase band fix can address.

### Verdict: **FAIL**
Readouts 3 and 6 fail on their own (gating: PASS requires 1, 2, 3, 6); readouts 1, 2 hold (2 for the
first time in the arc); readout 5 holds, less vacuously than before. `0ecbc66` is empirically
validated on its own direct target (chopper training) but the Scale meta as a whole is still far from
a working factory economy or a competitive result — avg boss wood 23.2 (need ≥55), 0/8 boss wins,
4/4 field losses worse than −150 (avg −403). No crashes; no HTTP 422s; probe compiled clean (full and
minified).

### Single most actionable observation
The B2.3 fix worked exactly as designed — readout 2 (HANDS), the direct target of both its band-order
fix and its grace window, now passes cleanly for the first time across four verdicts (n=4 EVER 7/8,
up from 0/8 last run) — so the band-collision and T_SWITCH-cliff diagnoses were correct and the fixes
should NOT be reverted. But getting the chopper to reliably train has now exposed the arc's next real
ceiling, which no further priority-band tuning will fix: the Scale ladder is hard-capped at n=4
forever (`SCALE_LADDER` has exactly 3 rungs, `want_hand` requires `n < 4`), so at most one chop=2
troll ever exists for the rest of any game, and — because `scale_funding` keeps outranking
Printer/plant work for the ladder's *entire* duration (up to t260 this run, or never-ending in 3/4
field games) — the farm cannot even start growing in earnest until the ladder is fully paid off,
squeezing the whole plant→mature→fell→bank pipeline into whatever turns remain (as little as 40 of
300). Even the single best-case game this run (n=4 at t150, the earliest possible) only gains 18 wood
in the following 150 turns, well under the ≥40 bar — evidence that raising the ladder's cap (add
post-t260 rungs so headcount can keep growing past 4, matching opponents who reach 5-8 trolls) or
letting some trolls do farm/printer work concurrently with the remainder still funding the ladder
(rather than every troll racing bands until the wallet is fully paid) is the next lever, not another
band-value adjustment.
