# Candidate v1.31.0-liq44 — Builder Report

**Task:** Task 1 (A1) — `GE_LIQ_T 34→44` — earlier endgame banking.
**Role executed:** BUILDER only (task-1-brief.md Steps 1–3 / pipeline-briefs.md builder-brief
steps 2–7). No games played, no arena submission — that is the gatekeeper's / arena-runner's job.
**Base tree:** working tree at the time of this task = arena-neutral twin of the reigning champion,
config `v1.28.3-sticky6` (confirmed clean, `git status` showed no pending changes before edits).
Champion artifact (`cgauto/submissions/v1.28.2-steady2.min.rs`) was **not touched**.

## 1. What changed

File: `rust/src/botmain.rs`. Two single-line `const` edits, exactly the two `sed` commands
specified in `task-1-brief.md` Step 1 — no other lines touched.

```diff
--- a/rust/src/botmain.rs
+++ b/rust/src/botmain.rs
@@ -8,7 +8,7 @@ use std::cell::RefCell;

 // ── constants ───────────────────────────────────────────────────────────────

-const VERSION: &str = "1.28.3-sticky6"; // STICKY 3->6 (coin-flip conversion attempt)
+const VERSION: &str = "1.31.0-liq44"; // A1 liquidation-timing knob
 // (the sequential cascade jobs.rs was REMOVED for submission size — 100 KB cap; it lives in
 // git history and in the frozen v1.26.0 artifacts for instant fallback)
 mod state;
@@ -89,7 +89,7 @@ const GE_FARM_R: i32 = 2; // v1.13.0: TIGHT farm hugging the shack — halves th
 const GE_FARM_MAX: usize = 12; // v1.19.0: fill the radius-2 area (~12 cells) — more trees maturing in parallel = chopper idles less
 const GE_FELL_SIZE: i32 = 2; // NATIVE/contested trees: fell at size 2 = DENIAL (grab before opponent)
 const GE_CHOP_R: i32 = 5; // v1.13.0 LIVE roam (GE_CHOP_R=3 was marginally better in bursts but within noise; kept 5)
-const GE_LIQ_T: i32 = 34; // turns_rem <= this: fell anything reachable
+const GE_LIQ_T: i32 = 44; // A1: bank standing value earlier (census: +4-margin coin-flips vs peers)
 const GE_STARTER_CHOP: bool = true; // let a chop-capable starter help fell
 const GE_MIN_TURNS_LEFT: i32 = 20; // no training inside the last 20 turns
 const GE_SEED_RESERVE: usize = 2; // protect K most-mature farm bananas as seed sources
```

Semantics: `GE_LIQ_T` gates the endgame liquidation phase ("turns_rem <= this: fell anything
reachable"). Raising it from 34 to 44 makes the bot enter full liquidation/banking mode 10 turns
earlier — the hypothesis being that standing wood value should be converted to banked score sooner
to win the "+4-margin" coin-flip games identified in the census. Pure tuning knob; no logic
branches added or removed, no other file touched.

## 2. Gate results (builder brief steps 2–7)

All commands were run with cwd = `/home/tarstars/prj/troll_farm/rust` unless noted. All gates
**PASSED**.

### Gate 1 — `cargo build --release`
```
cd rust && cargo build --release
```
Decisive line: `Finished release [optimized] target(s) in 6.58s`
0 compile errors. 4 pre-existing warnings, all unrelated to this diff (verified: they concern
dead-code/unused-variable lint on `HARVESTER` consts in `strategies/silver_boss.rs` and
`strategies/mybot.rs`, an unused `opp` binding, and an unused `Strategy` import in
`src/bin/fastcheck.rs` — none of these symbols are touched by the GE_LIQ_T/VERSION edit).

### Gate 2 — `cargo test --release`
```
cd rust && cargo test --release
```
Decisive line (suite count): `grep -c "test result: ok" ⇒ 20`
20/20 test binaries report `test result: ok`; 0 `FAILED`; 0 `error` lines in the full log.
Breakdown of the 20 suites: 15 unit-test harnesses (`src/lib.rs` + 14 `src/bin/*.rs` binaries,
all with 0 local `#[test]`s — expected, they're tool binaries), 4 integration suites
(`tests/motion_corridor.rs` = 2 passed, `tests/planner_solver.rs` = 3 passed,
`tests/planner_tasks.rs` = 3 passed, `tests/sim_engine_tests.rs` = 26 passed), plus 1 doc-test
suite (0 tests). Total: **34 individual tests passed, 0 failed.**

### Gate 3 — self-determinism
```
./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
```
Decisive line: `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`

### Gate 4 — bundle
```
uv run --no-sync python tools/bundle.py
```
Decisive line: `src/botmain.rs -> target/refactor/bundled.rs: 57554 chars (gate with rustc +
equality + minify)`

### Gate 5 — compile the bundled (dot-free) copy
```
cp target/refactor/bundled.rs <scratchpad>/l44cc.rs
rustc --edition 2021 -O l44cc.rs -o l44_bin
```
Decisive result: exit code `0`, empty stderr, binary produced
(`l44_bin`, 13,451,592 bytes). Compiles clean.

### Gate 6 — minify
```
uv run --no-sync python tools/minify.py target/refactor/bundled.rs ../cgauto/submissions/v1.31.0-liq44.min.rs
```
Decisive line: `57554 -> 38706 chars (67%)`
Size check: `wc -c` on the output = **38706 bytes** — under the 100000-byte cap with large margin
(≈61% headroom).

### Gate 7 — compile the minified (dot-free) copy
```
cp ../cgauto/submissions/v1.31.0-liq44.min.rs <scratchpad>/l44min.rs
rustc --edition 2021 -O l44min.rs -o l44min_bin
```
Decisive result: exit code `0`, empty stderr, binary produced
(`l44min_bin`, 13,451,656 bytes). Compiles clean.

## 3. Artifact sizes

| Artifact | Bytes | Notes |
|---|---|---|
| `cgauto/submissions/v1.31.0-liq44.rs` (full bundled) | 58,855 | `bundle.py` reports 57,554 *chars*; the byte count is larger because comments contain multi-byte UTF-8 (em dashes, arrows, multiplication sign), which is normal Python `len()` (chars) vs on-disk UTF-8 (bytes) — not an anomaly. |
| `cgauto/submissions/v1.31.0-liq44.min.rs` (minified, submission) | 38,706 | Matches `minify.py`'s own char count exactly (38706 chars = 38706 bytes ⇒ pure ASCII after minification, since comments are stripped) — well under the 100 KB cap. |

Both frozen to `cgauto/submissions/` and duplicated to
`data/candidates/v1.31.0-liq44/{v1.31.0-liq44.rs,v1.31.0-liq44.min.rs}` per the freeze step.
Sanity-verified: both frozen copies contain `const VERSION: &str = "1.31.0-liq44"` and
`GE_LIQ_T: i32 = 44` (grepped post-copy).

## 4. Anomalies

- `tools/bundle.py` / `tools/minify.py` live at `rust/tools/`, not a top-level `tools/` — the
  brief's commands are written relative to `rust/` as cwd, which is how they were run (consistent
  with builder-brief step 2's `cd rust && cargo build ...`). No actual problem, just noting the
  path base for whoever gates this next.
- No other anomalies. Build/test/equality/bundle/minify/compile all passed on the first attempt;
  no retries, no flaky results, no unrelated diffs picked up.

## 5. Scope discipline

- Champion artifact `cgauto/submissions/v1.28.2-steady2.min.rs` — untouched (not read or written).
- Only `rust/src/botmain.rs` was modified in the source tree; `git diff` before commit showed
  exactly the two lines above and nothing else.
- No games were played and nothing was submitted to the arena — out of scope for the builder role
  (gatekeeper/arena-runner stages, Steps 4–6 of the task brief, are explicitly NOT executed here).

## 6. Next steps (for the gatekeeper / arena-runner — not executed here)

Per `task-1-brief.md` Steps 4–6: gatekeeper dispatch with `VERSION=v1.31.0-liq44`,
`FIELD_IDS=6480914,6480966`, `PHASE_INVARIANTS=none (Tempo knob; check @TFFARM flaps stay ≤15)`;
then arena-runner on PASS; then analyst with the verdict.

## Gatekeeper verdict (v1.31.0-liq44)

**Run:** 2026-07-07 10:09 MSK. Role executed: GATEKEEPER only (no arena submit).

### DEBUG probe build
- `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on
  `data/candidates/v1.31.0-liq44/v1.31.0-liq44.rs` → diff confirmed **exactly one line** changed
  (the DEBUG const; verified via `diff`).
- Minify: `57553 -> 38705 chars (67%)` (one char shorter than the release build's 57554→38706,
  consistent with `false`→`true` being one character shorter — expected, not an anomaly).
- Compile-check (dot-free copy, `rustc --edition 2021 -O`): exit 0, binary produced → **DBG-MIN-OK**.
- DEBUG `.min.rs` used for all games below (scratchpad path, not committed — per §2 rule 3,
  DEBUG builds are never frozen/submitted).

### Boss batch (8/8 games collected, no HTTP 422, no retry needed)

`ramp.py --last 8`:
```
t75 : us   8.9  opp   1.8  delta  +7.1
t150: us  21.0  opp  13.2  delta  +7.8
t225: us  32.5  opp  29.4  delta  +3.1
t300: us  44.6  opp  52.4  delta  -7.8
AGGREGATE: wins 1/8 (12%)  our avg final wood 44.6  late gain us +12.1 vs opp +23.0
```
Per-game (gameId, W/L, final wood us-opp, late-quarter t225→t300 gain us/opp):

| gameId | W/L | final wood | late gain us | late gain opp |
|---|---|---|---|---|
| 895358254 | W | 50.0–50.0 | +14.0 | +14.0 |
| 895358277 | L | 51.0–62.0 | +15.0 | +36.0 |
| 895358296 | L | 40.0–45.0 | +12.0 | +16.0 |
| 895358313 | L | 46.0–58.0 | +12.0 | +19.0 |
| 895358333 | L | 40.0–46.0 | +10.0 | +24.0 |
| 895358371 | L | 38.0–57.0 | +10.0 | +23.0 |
| 895358388 | L | 52.0–57.0 | +14.0 | +24.0 |
| 895358407 | L | 40.0–44.0 | +10.0 | +28.0 |

No crash: all 8 fresh `.log` files have a full 300 data rows (verified `grep -vc '^#'` = 300 for
each) and zero all-dash rows (verified with a dash-row grep = 0 for each).

Flaps telemetry (last `flaps=` value per fresh `.raw` file, `@TFFARM`):

| gameId | flaps (last value) |
|---|---|
| 895358407 | 11 |
| 895358388 | 14 |
| 895358371 | 5 |
| 895358333 | 8 |
| 895358313 | 5 |
| 895358296 | 1 |
| 895358277 | 6 |
| 895358254 | 5 |

8/8 games ≤15 flaps (bar: ≥6 of 8).

### Field batch (4/4 games collected, no HTTP 422, no retry needed)

vs **mikdiet** (agentId 6480914, Gold rank 119, score 18.2 — denial-style), 2 games:
| gameId | result | wood us–opp | score us–opp | margin |
|---|---|---|---|---|
| 895358445 | LOSS | 56–52 | 231–259 | −28 |
| 895358486 | LOSS | 64–90 | 263–372 | −109 |

vs **plcc** (agentId 6480966, Gold rank 104, score 19.9 — ≥19.0 target), 2 games:
| gameId | result | wood us–opp | score us–opp | margin |
|---|---|---|---|---|
| 895358504 | LOSS | 90–105 | 365–422 | −57 |
| 895358517 | LOSS | 69–114 | 288–461 | **−173** |

Field total: **0/4 wins**. One blowout: game 895358517 vs plcc, score margin **−173**, worse
than the −150 bar. (Both field opponents ran 4–5-troll builds vs the boss's typical 2-troll
build — a materially different, larger-scale opponent economy; noted for context, not a mitigant.)

### LIQ-specific readout (informational, not a gate)

Wood gained from t≈266 → t300 (the fixed 34-turn window; chosen because it equals the OLD
`GE_LIQ_T`=34 liquidation window, giving an apples-to-apples "final-window" comparison), from
the 8 fresh boss `.log` files. Note: the per-turn `.log` files here have full 1-turn granularity
(verified: every turn 1–300 present, no gaps), so "second-to-last vs last row" was read as
t266 vs t300 explicitly rather than literally row[-2]/row[-1] (which would be t299/t300).

| gameId | wood@t266 | wood@t300 | gain |
|---|---|---|---|
| 895358407 | 34 | 40 | +6 |
| 895358388 | 46 | 52 | +6 |
| 895358371 | 34 | 38 | +4 |
| 895358333 | 34 | 40 | +6 |
| 895358313 | 42 | 46 | +4 |
| 895358296 | 34 | 40 | +6 |
| 895358277 | 42 | 51 | +9 |
| 895358254 | 42 | 50 | +8 |

**Average final-34-turn wood gain: +6.1** (range +4..+9). Historical era value ≈ +8-12 → this
run is *below* that range, i.e. no evidence the earlier-liquidation knob banked more standing
value inside this fixed window. Reported per instructions; not a gate.

### Gate-by-gate check

| Criterion | Bar | Measured | Result |
|---|---|---|---|
| Boss avg final wood | ≥45 | 44.6 | **FAIL** (marginal, −0.4) |
| t300 delta | not worse than −15 | −7.8 | PASS |
| Game crash | none | 0/8 (full 300-row logs, no dash rows) | PASS |
| Flaps ≤15/game | in ≥6 of 8 | 8/8 | PASS |
| Field blowout | no loss worse than −150 | −173 (plcc g2) | **FAIL** |

### Verdict: **FAIL**

Two independent bar violations: (1) boss avg final wood 44.6 is fractionally under the ≥45 bar
(a ~1% miss, arguably noise over 8 games); (2) one field game vs plcc lost by score margin −173,
exceeding the −150 blowout bar by 23 — this one is not marginal. Per the brief's FAIL rule, either
alone renders the candidate FAIL; both fired. Boss win rate 1/8 (12%) is roughly flat vs the
historical-era 14% baseline (contextual only, not a gate). Do not promote to arena-runner as-is.
