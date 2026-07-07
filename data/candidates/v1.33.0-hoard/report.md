# Candidate v1.33.0-hoard — Builder Report

**Task:** Task 3 (B2) — hoard bands + wallet ladder: fell-suppression with a denial-emergency
exception, a wallet-building harvest band, and the Scale training ladder.
**Role executed:** BUILDER only (`.superpowers/sdd/task-3-brief.md` Steps 1–6 /
`docs/superpowers/plans/pipeline-briefs.md` builder-brief steps 1–7, TDD-style), per the
dispatching agent's explicit resolutions of the brief's ambiguities. Step 7 ("gatekeeper, Scale
build" — play boss 8 + field 4 games) is a **separate role**, out of scope here; see §6.
**Base tree:** working tree at the start of this task = `v1.32.0-phases` (Task 2, phase skeleton),
confirmed clean (`git status` showed no pending changes before edits). Champion artifact
`cgauto/submissions/v1.28.3-sticky6.min.rs` — read only, never touched.

## 1. What changed

TDD process (task-3-brief.md Steps 1–4), exactly as specified:

1. **Wrote the failing tests** at `rust/tests/phase_hoard.rs` (verbatim from the brief; helpers
   `base_state()/starter()/chopper()/banana()` copied VERBATIM from `tests/planner_tasks.rs`,
   `base_plan()` copied with one change: `phase: Phase::Hoard`).
2. **Ran it, confirmed the expected failure pattern** (the brief calls this out explicitly: "the
   first meaningfully"):
   ```
   test hoard_denial_emergency_fells_threatened_tree ... ok
   test hoard_suppresses_fells_without_threat ... FAILED
   thread '...' panicked: hoard must not fell an unthreatened tree: MOVE 2 3 2
   ```
   Exactly as predicted: pre-implementation, `Phase::Hoard` existed (Task 2) but nothing read it
   in `planner.rs`, so the chopper always fells regardless of phase — test 1 (must NOT fell)
   fails meaningfully; test 2 (must fell when threatened) passes vacuously (it always fells).
3. **Implemented** in `rust/src/botmain/planner.rs` and `rust/src/botmain/tactics.rs`, per the
   dispatching agent's binding resolutions (below).
4. **Full suite green** (Gate 2).

### Binding resolutions followed (verbatim intent from the dispatch)

- **Tempo inertness is the prime rule.** Every new band/gate/tactic keys on `plan.phase` (or
  `Meta::Scale` at plan-time in `tactics.rs`). Verified: flag-off equality vs
  `v1.28.3-sticky6.min.rs` is EQUAL over 25 seeds (Gate 8).
- **`threatened()` efficiency:** ONE multi-source BFS per `candidates()` call
  (`bfs_distances(&state.walkable, &state.opp_trolls…)`), computed lazily as `Option<HashMap>`
  only when `plan.phase == Phase::Hoard` — zero extra cost on the live Tempo path.
- **Hoard suppresses ONLY the four fell-type bands**: chopper fell (72/70), chopper
  anti-starvation (31/30), starter chop-help (42/40), starter anti-starvation (31/30-nested).
  Each gated `if hoard && !threatened(pc) { continue; }`. Bank/plant/harvest/pick/seed/park bands
  untouched.
- **Hoard wallet band** (starter-branch, chop_power < 2): new band, value `62 * BAND -
  eta(&d, pc, ms)`, `MoveTo` any tree with `p.fruits > 0 && d.contains_key(&p.pos())`; the
  standing-harvest band's `want` extended with `|| plan.phase == Phase::Hoard`.
- **Scale training ladder** (`tactics.rs`): under `Meta::Scale`, `want_chopper` forced `false`;
  `SCALE_LADDER: [(i32,i32,i32,i32);3] = [(1,1,1,0),(1,1,1,0),(2,2,0,2)]`, min turns
  `[10,40,110]`, `slot = ((n-1).max(0) as usize).min(2)` (the `.max(0)` is a defensive floor
  against a hypothetical `n=0` — never true in real play since a troll always exists — that
  keeps `(n-1)` from wrapping to a huge `usize` and panicking on array index; identical to the
  brief's literal formula for every real `n >= 1`), `want_hand = n < 4 && state.turn >=
  SCALE_MIN_TURN[slot]`. Mapped onto the EXISTING `Plan` fields (`want_feeder = want_hand`,
  `train_spec = SCALE_LADDER[slot]`, `cost/train_now/need_iron/need_fund` exactly as specified)
  — **no new `Plan` fields**, so `planner.rs` needed zero struct changes for the ladder itself.
  The Tempo branch is the pre-existing code, unchanged, now living in the `else` arm.

Files touched:

- `rust/src/botmain/planner.rs`: import `Phase` alongside `Plan`; new `hoard`/`enemy_d`/
  `threatened` block at the top of `candidates()`; `if hoard && !threatened(pc) { continue; }`
  guards inserted into the 4 fell-type loops; standing-harvest `want` extended; new Hoard wallet
  band inserted between the standing-harvest band and the FUNDING section.
- `rust/src/botmain/tactics.rs`: the training-var block (`want_chopper`…`need_fund`) restructured
  into an `if super::GE_META == Meta::Scale { … } else { <BYTE-IDENTICAL pre-B2 code> }` tuple
  destructure.
- `rust/src/botmain.rs`: `VERSION` -> `"1.33.0-hoard"`; `GE_META` doc comment updated to describe
  the now-real Hoard behavior (was: "ships the machinery with ZERO behavior change" — B1's
  wording, now stale since B2 gives Scale real bands; Tempo itself is still behavior-frozen).
- `rust/tests/phase_hoard.rs`: **new** — the two tests from the brief.

Full diff of the three modified files (198 lines) saved at
`/tmp/claude-1001/-home-tarstars-prj-troll-farm/402b95ba-f2eb-4014-9080-85c2c1e9d9a7/scratchpad/task3.diff`
during this session; key hunks:

```diff
--- a/rust/src/botmain/planner.rs
+++ b/rust/src/botmain/planner.rs
@@ use super::tactics::Plan;
+use super::tactics::{Phase, Plan};
@@ let mut out: Vec<Cand> = Vec::new();
+    let hoard = plan.phase == Phase::Hoard;
+    let enemy_d: Option<HashMap<Cell, i32>> = if hoard {
+        Some(bfs_distances(&state.walkable,
+            &state.opp_trolls.iter().map(|e| e.pos()).collect::<Vec<_>>()))
+    } else { None };
+    let threatened = |pc: Cell| -> bool {
+        enemy_d.as_ref().map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
+    };
@@ (x4: chopper fell/anti-starve, starter chop-help/anti-starve)
+            if hoard && !threatened(pc) {
+                continue; // Hoard: no fells unless the tree is under denial threat
+            }
@@ standing-harvest want
-                            ...))));
+                            ...)))
+                    || plan.phase == Phase::Hoard;
@@ new band, inserted before "// 4) FUNDING"
+        if plan.phase == Phase::Hoard {
+            for p in state.trees.iter().filter(|p| p.fruits > 0 && d.contains_key(&p.pos())) {
+                let pc = p.pos();
+                out.push(Cand { kind: Kind::MoveTo, target: Some(pc),
+                    value: 62 * BAND - eta(&d, pc, ms) });
+            }
+        }

--- a/rust/src/botmain/tactics.rs
+++ b/rust/src/botmain/tactics.rs
@@ let nchop = ...;
-    let want_chopper = nchop == 0 && (...);
-    ... (7 lines, unchanged logic) ...
-    let need_fund: [bool; 3] = [...];
+    let (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund) =
+        if super::GE_META == Meta::Scale {
+            const SCALE_LADDER: [(i32,i32,i32,i32);3] = [(1,1,1,0),(1,1,1,0),(2,2,0,2)];
+            const SCALE_MIN_TURN: [i32; 3] = [10, 40, 110];
+            let slot = ((n - 1).max(0) as usize).min(2);
+            let want_hand = n < 4 && state.turn >= SCALE_MIN_TURN[slot];
+            ... (spec/cost/train_now/need_iron/need_fund per the ladder) ...
+            (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund)
+        } else {
+            <the pre-existing 7 lines, byte-identical> ...
+            (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund)
+        };

--- a/rust/src/botmain.rs
+++ b/rust/src/botmain.rs
-const VERSION: &str = "1.32.0-phases";
+const VERSION: &str = "1.33.0-hoard";
```

## 2. Gate results (pipeline-briefs.md builder-brief steps 2–7)

All commands run with cwd = `/home/tarstars/prj/troll_farm/rust` unless noted.

### Gate 1 — `cargo build --release`
`Finished release [optimized] target(s) in 7.23s`. 0 compile errors. Only pre-existing warnings
(unused `PLUM` import in `printer_bot.rs`, unused `opp` in `boss_v3.rs`, unused `HARVESTER` consts
in `silver_boss.rs`/`mybot.rs`, unused `Strategy` import in `fastcheck.rs`) — none touch this diff.

### Gate 2 — `cargo test --release`
`grep -c "test result: ok"` -> **22** suites (was 21 after Task 2, +1 for the new `phase_hoard.rs`
suite). `grep -c FAILED` -> **0**. Sum of all `N passed` -> **38** individual tests (was 36, +2 =
the new `phase_hoard` tests). New suite's own output:
```
Running tests/phase_hoard.rs
running 2 tests
test hoard_denial_emergency_fells_threatened_tree ... ok
test hoard_suppresses_fells_without_threat ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```
All pre-existing suites unaffected, including `tests/planner_tasks.rs` (3 passed, unchanged) and
`tests/phase_skeleton.rs` (2 passed, unchanged — Task 2's Meta/Phase-plumbing tests).

### Gate 3 — self-determinism
```
./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
```
`EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`

### Gate 4 — bundle
```
uv run --no-sync python tools/bundle.py
```
`src/botmain.rs -> target/refactor/bundled.rs: 62586 chars (gate with rustc + equality + minify)`

### Gate 5 — compile the bundled (dot-free) copy
`rustc --edition 2021 -O <scratch>/bundled_v1330.rs -o <scratch>/bundled_v1330_bin` -> exit 0, no
stderr, 13,456,016-byte binary. Compiles clean.

### Bonus gate (bundle-inlining sanity, per `bundle.py`'s own docstring)
```
./target/release/equality <scratch>/bundled_v1330_bin target/release/bot 8 300 target/release/bot
```
`EQUAL: 16 games (8 seeds x 2 seats), all command streams identical` — bundling introduced no
drift vs the lib-built binary.

### Gate 6 — minify
```
uv run --no-sync python tools/minify.py target/refactor/bundled.rs cgauto/submissions/v1.33.0-hoard.min.rs
```
`62586 -> 41530 chars (66%)`. `wc -c` confirms **41530 bytes** — 58% under the 100,000-byte cap
(same margin class as the precedent candidate).

### Gate 7 — compile the minified (dot-free) copy
`rustc --edition 2021 -O <scratch>/frozen_min_v1330.rs -o <scratch>/frozen_min_v1330_bin` -> exit 0,
no stderr, 13,456,176-byte binary. Compiles clean. The exact frozen full `.rs` was compile-checked
the same way earlier (Gate 5).

### Gate 8 — **THE gate**: flag-off equality vs the champion (`v1.28.3-sticky6.min.rs`)

Per the dispatching agent's binding resolution ("label-match the VERSION string first, exactly
like Task 2's report shows... use v1.28.3-sticky6, not the brief's stale v1.28.2 pointer"):
```
cp cgauto/submissions/v1.28.3-sticky6.min.rs <scratch>/champ.rs
rustc --edition 2021 -O <scratch>/champ.rs -o <scratch>/champ_bin
sed 's/1\.33\.0-hoard/1.28.3-sticky6/' target/refactor/bundled.rs > <scratch>/lm.rs
rustc --edition 2021 -O <scratch>/lm.rs -o <scratch>/lm_bin
./target/release/equality <scratch>/champ_bin <scratch>/lm_bin 25 300 <scratch>/champ_bin
```
Decisive line: **`EQUAL: 50 games (25 seeds x 2 seats), all command streams identical`**

This is the run that proves the task's central claim: with `GE_META = Meta::Tempo` live, adding
the Hoard bands + the Scale ladder changes **nothing**, byte-for-byte, across every command line
CG's stdout protocol would carry, for 50 full games.

**Extra verification (not in the enumerated gate list, done for rigor):** diffed every `const `
declaration between the champion `.min.rs` and the new bundle (`grep -oE "const [A-Z_0-9]+: [^=]+=
[^;]+;" … | sort | diff`). The only differences are **additive**: `GE_META` (Task 2), `T_SWITCH`
(Task 2), and this task's new `SCALE_LADDER`/`SCALE_MIN_TURN` consts, plus the expected `VERSION`
string. No pre-existing tunable const drifted — confirms the equality result isn't hiding a
same-turn-1-divergence coincidence.

## 3. Artifact sizes

| Artifact | Bytes | Notes |
|---|---|---|
| `cgauto/submissions/v1.33.0-hoard.rs` (full bundled) | 63,901 | disk bytes > `bundle.py`'s 62,586 *chars* — multi-byte UTF-8 in comments (em dashes, arrows), same pattern as every prior frozen artifact. |
| `cgauto/submissions/v1.33.0-hoard.min.rs` (minified, submission) | 41,530 | matches `minify.py`'s own char count exactly (pure ASCII post-minification) — 58% under the 100 KB cap. |

Both frozen to `cgauto/submissions/` and duplicated to
`data/candidates/v1.33.0-hoard/{v1.33.0-hoard.rs,v1.33.0-hoard.min.rs}`. Sanity-verified in both
frozen copies: `const VERSION: &str = "1.33.0-hoard"` (1 hit each), `SCALE_LADDER` present in both.

## 4. Anomalies

- **The dispatch's "feeder-errand funding band (52/51, `turn < 150` gate)" claim does not match
  the repository.** The actual, sole existing funding band in `planner.rs` is
  `let (fund_hi, fund_lo) = if plan.want_chopper { (60, 58) } else { (45, 44) };` gated by
  `plan.want_chopper || plan.want_feeder` — **no `state.turn < 150` gate exists anywhere** (grepped
  `"150"` across every `botmain*.rs` file: zero hits). I verified this isn't something I missed by
  re-reading the whole file (378 lines) and grepping `fund_hi|fund_lo|52 \*|51 \*|150` before
  concluding. The dispatch's own instruction for this item was "leave it as-is" (a no-op), which I
  honored literally — I did not touch the funding section at all. The ladder's `want_feeder = true`
  correctly drives the REAL existing band (45/44) to fund the next hand's fruit cost; the mechanism
  the resolution points at ("will serve the ladder via want_feeder") works exactly as intended, just
  at the actual band values (45/44), not the stated (52/51), and unconditionally rather than under a
  `turn<150` gate that doesn't exist. Flagging per the "trust but verify" precedent Task 2 set with
  its stale-champion-pointer finding — not a defect introduced by this candidate, and no action was
  needed since the resolution's actual instruction was to leave the section alone.
- **Step 7 ("gatekeeper, Scale build") is explicitly a different role** and out of scope for this
  builder pass — no boss/field games were played, no arena action taken. As a courtesy (the brief
  says "**builder** makes a SCALE probe"), I built one: `sed` `DEBUG`->`true` and `GE_META`->
  `Meta::Scale` on the bundled source, minified it, rustc-compile-checked it (exit 0), and
  smoke-tested it directly over the wire protocol for 15 turns with a single starter troll and an
  empty map — no crash/panic, and `@TFFARM t=5 farm=0 seeds=0 n=1 flaps=0 phase=Hoard` confirmed the
  phase telemetry fires correctly under the Scale meta. Saved to
  `data/candidates/v1.33.0-hoard/v1.33.0-hoard.scale-debug-probe.min.rs` (41,529 bytes) for whoever
  picks up the gatekeeper role next. **I did not run boss/field games with it** — that needs the
  `collect_debug_games.py` dispatch + real API calls, explicitly the gatekeeper's job, and per
  `docs/ROADMAP.md` §2 rule 7 (play-API throttle discipline) I did not want to spend that budget
  without being asked.
- `tools/bundle.py`/`tools/minify.py` live at `rust/tools/`, not a top-level `tools/` — same note as
  both precedent candidates; commands here were run relative to `rust/` as cwd.
- No other anomalies. TDD failing-test step failed for the intended reason (missing suppression
  logic, not a typo/setup mistake); all subsequent gates passed on the first attempt after
  implementation.

## 5. Scope discipline

- Champion artifact (`v1.28.3-sticky6.*`) — read only, never written.
- Only `rust/src/botmain.rs`, `rust/src/botmain/planner.rs`, `rust/src/botmain/tactics.rs` modified
  in the source tree; `rust/tests/phase_hoard.rs` added. `git diff --stat` before freezing showed
  exactly these three files (89 insertions / 22 deletions), and nothing else.
- `docs/ROADMAP.md` §2 rule 10 respected: no changes to `game/engine.rs`, any existing
  `cgauto/submissions/*` file, or `rust/src/botmain/motion.rs`.
- No games played against the real API, nothing submitted to the arena — out of scope for the
  builder role.

## 6. Next steps

Per `task-3-brief.md` Step 7: dispatch a **gatekeeper** for the Scale probe
(`data/candidates/v1.33.0-hoard/v1.33.0-hoard.scale-debug-probe.min.rs`, DEBUG=true, GE_META=Scale,
compile-checked, smoke-tested) — `collect_debug_games.py <probe> boss 8` + field 4 (>=1 denial-style
opponent, >=1 >=19.6 player per the gatekeeper brief), checking: `@TFPHASE`/`@TFFARM` shows
Hoard->Factory at t140; hands >=2 trained by t140 in >=6/8 games; zero CHOP commands before t140
except denial (spot-check 2 raws); lemon banked >= ladder cost by t100. **This gate can FAIL without
blocking Task 4** (bands iterate) per the brief. Task 4 (B3, factory bands) can now build on
`Plan.phase == Phase::Factory` the same way this task built on `Phase::Hoard`; the Scale ladder's
slot-2 hand (`(2,2,0,2)`, chop=2) will become a real chopper once trained, so Task 4's factory
bands need to handle a variable troll roster (not just "the chopper" singular).
