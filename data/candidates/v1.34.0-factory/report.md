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
