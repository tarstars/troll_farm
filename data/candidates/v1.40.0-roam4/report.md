# Candidate v1.40.0-roam4 — Builder Report

**Task:** A one-const sweep on the planner architecture: `GE_CHOP_R` 5 -> 4 (tighten the
chopper's roam radius by 1, a travel-cut retest). Motivation (analyst `b62c977` queue #2, and
the analyst's closing note on `v1.39.0-sharepen4`'s report: *"Queue #2 (chop_r 5→4) is
unaffected by this result and remains the correct next submit"*): the sequential-cascade era
(pre-R6b planner) measured `GE_CHOP_R=3` as "marginally better in bursts but within noise"
against `GE_CHOP_R=5` and kept 5 live — but that verdict predates the R6b joint planner
(bands/`within_roam`/`own_half`/the race check) entirely, so it doesn't transfer. This candidate
retests one step down (4, not 3) on the current planner. Builder role only; no interaction with
the race check intended (roam gates which trees are even CANDIDATES for the primary fell bands;
race gates contested candidates that already passed the roam/own_half gate — orthogonal
concerns, confirmed in the TDD construction below where `race_pen=0` throughout).

**Worktree state (pre-task, resolved):** `git log --oneline -1` showed `fa33b21` ("feat: sim
Bronze support + tuned wood economy (v0.6.1)") — stale, 197 commits behind the required base
`c8ebda9`. Verified `fa33b21` is a strict ancestor of `session-2026-07-01`'s tip via `git
merge-base --is-ancestor fa33b21 session-2026-07-01` (exit 0), confirmed a clean working tree
(`git status`: nothing to commit), then fast-forwarded with `git merge --ff-only
session-2026-07-01` (no rebase, no history rewrite). Landed on `c2ffec7` ("arena:
v1.39.0-sharepen4 KEEP at parity (17.6 == 17.6 bracket)"), confirmed a descendant of `c8ebda9`
via `git merge-base --is-ancestor c8ebda9 HEAD` (exit 0) — the required base commit, with no
intervening drift beyond the already-landed `v1.39.0-sharepen4` (`RACE_SHARE_PEN=4`,
`DENY_W=0`), which this candidate carries forward unchanged per the task's BASE NOTE.

## What changed

Both edits live entirely in `rust/src/botmain.rs`; no other file's *production* code was
touched (only the new test file, below).

```rust
const VERSION: &str = "1.40.0-roam4"; // GE_CHOP_R 5->4 roam retest on the planner (analyst b62c977 queue #2)
...
const GE_CHOP_R: i32 = 4; // roam retest on the planner (travel-cut; cascade-era noise verdict doesn't transfer; analyst b62c977 queue #2)
```

`GE_CHOP_R` feeds `tactics.rs`'s `plan_impl`: `let chop_r = if econ_b { 10 } else { GE_CHOP_R };`
(`econ_b` is a permanent `false` live) — so `plan.chop_r` drops 5->4 unconditionally. `chop_r` is
consumed in exactly one place, `planner.rs`'s `within_roam` closure (`farm_d(tree) <= chop_r`),
which gates the PRIMARY fell bands (70/72, both the chopper's own candidates and the starter's
chop-help band 40/42) alongside `own_half`. It does NOT gate the anti-starvation fallback (band
30/31, `p.size >= 1` only) — that asymmetry is exactly what the new test exploits.

## TDD

### RED first — `rust/tests/roam.rs` (new file)

Per the task's own worked construction, checked directly against the `candidates()` source
(`rust/src/botmain/planner.rs`) before writing anything: a single-tree construction cannot
observe the roam change (the anti-starvation band would still reach a dist-5 tree regardless of
`chop_r`, since band 30 ignores roam entirely). The observable needs a SECOND tree that is
*always* anti-starvation-only (never eligible for band 70 regardless of `chop_r`) so the
boundary tree's band-70->30 demotion has something concrete to lose to. Construction used:

- Own-half fellable banana at `(3,4)`: `manhattan(shack=(0,2)) = 5 <= manhattan(opp=(7,2)) = 6`
  -> `own_half=true`. `farm_d` (BFS from the shack; open 8x5 grid == manhattan here) `= 5`, so
  `within_roam` only while `chop_r >= 5`.
- Enemy-half fellable banana at `(4,2)`: `manhattan(shack) = 4`, `manhattan(opp) = 3` ->
  `own_half=FALSE` unconditionally, independent of `chop_r` -> perpetually anti-starvation-only
  (band 30), never band 70/72.
- Chopper at `(1,2)` (shack-adjacent), `movement_speed` struct-updated `2->1` (same convention as
  `tests/race_check.rs`'s `share_pen_shifts_near_tie_to_free_tree`) so the two map-distances (4
  and 3 from the chopper's own position) map to etas 4 and 3 without an integer-division tie (at
  the `chopper()` helper's native `ms=2` both etas round up to 2 and the test cannot distinguish
  the two trees). Both trees are identical size-2 bananas (same health -> same `chop_t=2`).
- Used `tactics::plan_with_meta(&st, &my, Meta::Tempo)` — the existing test-only seam — rather
  than a hand-built `Plan` with a hardcoded `chop_r` field (the convention every other test file
  in this repo uses via `base_plan()`). This makes the test a genuine regression check tied to
  the ACTUAL compiled `GE_CHOP_R` constant (since `GE_META` is fixed at `Meta::Tempo` live,
  `plan_with_meta(..., Meta::Tempo)` computes byte-identically to `tactics::plan()`), not merely
  a check of `planner::assign`'s generic roam-gating logic against an arbitrary injected number.

Ran `cargo test --release --test roam` with the test added and `GE_CHOP_R` still `5` (unedited):

```
thread 'tight_roam_drops_boundary_tree_to_enemy_half_rival' panicked at tests/roam.rs:84:5:
tightened roam (GE_CHOP_R=4) must send the chopper to the enemy-half tree at (4,2) once the own-half tree at (3,4) falls outside roam: got MOVE 2 3 4
test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Exactly the predicted failure (`MOVE 2 3 4`, the own-half boundary tree, chosen via its band-70
candidate which dwarfs any band-30 value since `BAND=100_000`) — confirms the test is a true RED
against the live champion const, not a vacuously-true assertion.

### GREEN — after `GE_CHOP_R: 5 -> 4`

```
test tight_roam_drops_boundary_tree_to_enemy_half_rival ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Manual value check confirms this isn't a lexicographic tie-break artifact: under `chop_r=4`,
`(3,4)` drops to band 30 only (`30*BAND-(4+2) = 2,999,994`); `(4,2)` is band-30-only regardless
(`30*BAND-(3+2) = 2,999,995`) — `(4,2)` wins by 1 on ETA, a real value comparison, not a target-
ordering tie-break.

## Gate results

1. **Baseline** (tree as landed, pre-edit, with the new `roam.rs` test file present but
   `GE_CHOP_R` still `5`): confirmed 27 pre-existing suites (15 empty unittest bins + 11
   integration test files + 1 doctest) all green *before* adding `roam.rs`; identical to the
   `v1.39.0-sharepen4` report's own closing baseline (52 passed + 5 ignored + 0 failed).
2. **RED — `roam.rs`** (new test added, `GE_CHOP_R` still `5`): 1 FAILED, exact message quoted
   above.
3. **GREEN — `cargo build --release`** (post edit): clean — the same 5 pre-existing warnings as
   the `sharepen4` baseline (`PLUM` unused import in `printer_bot.rs`, `opp` unused variable in
   `boss_v3.rs`, `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`, `Strategy` unused
   import in `fastcheck.rs`) — confirmed via a full rebuild (`touch src/botmain.rs && cargo build
   --release`) and diffed against the pre-edit list. **No new warnings.**
4. **GREEN — `cargo test --release`** (post edit): **28 suites** (27 + the new `roam.rs`), **53
   passed** (52 + `roam.rs`'s 1) **+ 5 ignored + 0 failed**. Every other suite's count unchanged:
   `deny_probe` 0+1 ignored, `motion_corridor` 2, `nanaflow` 2, `phase_factory` 1, `phase_hoard`
   7, `phase_skeleton` 2, `planner_solver` 3, `planner_tasks` 3, `race_check` 3,
   `sim_engine_tests` 26, `tactics_scale` 3+4 ignored.
5. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8 300
   target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
6. **`tools/bundle.py`**: `src/botmain.rs -> target/refactor/bundled.rs: 74414 chars`. Grep
   confirms `VERSION: &str = "1.40.0-roam4"` and `const GE_CHOP_R: i32 = 4;` (single occurrence
   each, at the expected lines).
7. **`rustc --edition 2021 -O`** on the bundled source (dot-free copy): exit 0 (SRC-COMPILE-OK).
8. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8 seeds x
   2 seats), all command streams identical`.
9. **`tools/minify.py`**: `74414 -> 43649 chars (58%)` — 56% under the 100,000 B cap.
10. **`rustc --edition 2021 -O`** on the minified copy (dot-free copy): exit 0 (MIN-COMPILE-OK).
11. **Minified bin vs `target/release/bot`**: `EQUAL: 16 games (8 seeds x 2 seats), all command
    streams identical`.
12. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Minified: `74413 ->
    43648 chars (58%)` (1 byte shorter than the release `.min.rs`, same `false`->`true` length
    delta seen on every prior candidate's probe). `rustc --edition 2021 -O` compile-check: exit 0
    (DBG-COMPILE-OK). 2-seed local smoke: `./target/release/equality <probe> target/release/bot
    2 300 target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical` (no crash; DEBUG only echoes to stderr, so stdout-parity holds).
13. **Champion-equality: N/A by design**, same reasoning as the prior two behavior-changing
    sweeps (`v1.38.0-deny1`, `v1.39.0-sharepen4`) — this candidate intentionally changes fell-
    targeting for trees sitting at `farm_d` exactly 5 cells from the shack (the band that drops
    out of roam). Attempted an informative (non-required) cross-binary check — compiled the
    immediately-prior champion (`cgauto/submissions/v1.39.0-sharepen4.rs`) and ran `equality`
    against the new candidate at 8 seeds — but this is confounded: turn 1 always emits `MSG
    <VERSION>;...` and the `VERSION` string itself differs, so `equality` (which compares whole
    command lines) reports a "divergence" at turn 1 on every seed regardless of whether the roam
    logic differs downstream. Not included as evidence for that reason. Self-determinism (gate 5)
    and the bundle/minify round-trip equalities (gates 8, 11) already establish full determinism
    and shuffle-invariance; that is a different, weaker guarantee than champion-equality and is
    not conflated with it here.

## Sizes

- `cgauto/submissions/v1.40.0-roam4.rs`: **75,791 B** (bundled, comments retained).
- `cgauto/submissions/v1.40.0-roam4.min.rs`: **43,649 B** (56% under the 100,000 B cap).
- `data/candidates/v1.40.0-roam4/v1.40.0-roam4.rs` / `.min.rs`: byte-identical (`cmp`-verified)
  to the `cgauto/submissions/` copies above.
- `data/candidates/v1.40.0-roam4/v1.40.0-roam4.debug-probe.min.rs`: **43,648 B** (DEBUG=true; 1
  byte shorter than the release `.min.rs`).

## Diffstat

```
rust/src/botmain.rs  |  4 ++--   (VERSION + GE_CHOP_R only, 2 lines changed)
rust/tests/roam.rs   | 91 +++++++++++++++++++++++++++++++++++++++++++++++++  (new file)
2 files changed, 92 insertions(+), 2 deletions(-)  (approx.; roam.rs is new/untracked)
```

## Scope discipline

Only `GE_CHOP_R` and `VERSION` were touched in production code — a single one-const sweep, per
the task brief. NOT touched: `GE_FARM_R`/`GE_FARM_MAX` (farm geometry), `RACE_SHARE_PEN`/
`DENY_W` (race check / denial-weight probe, both carried forward from `v1.39.0-sharepen4` at
their current values as instructed), `own_half`'s manhattan gate, `fell_ok`/`seed_cells`
protection logic, `STICKY`, `GE_MAX_TROLLS`/training/`tactics.rs`'s ladder logic, or `motion.rs`.
Confirmed no interaction with the race check: in the TDD construction both candidate trees have
no opponent troll occupying them, so `race()` returns `Some(0)` (no penalty) for both, throughout
— the roam and race mechanisms are demonstrably orthogonal in this test, matching the task's
framing ("roam gates which trees are candidates; race gates contested ones").

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` then vs field (incl. >=1 denial-style
opponent — mikdiet 6480914 / plcc 6480966 — and >=1 >=19.6 player per `field_targets.py`). Read
`cgauto/ramp.py --last 8` (wood >=45, t300 delta vs -15.3 baseline) and telemetry from the newest
`.raw` files (`@TFFARM` / `@TFPHASE`). Expected signature: this is a pure travel-cut retest of an
already-proven mechanism (`within_roam`'s structure is unchanged, only the radius shrinks by 1),
so real maps are much larger than the 8x5 unit-test grid — the effect size should scale with how
often trees sit in the vacated `farm_d ∈ (GE_FARM_R, 5]` ring on the far side of the shack from
the farm core, which the cascade-era measurement (radius 3 vs 5, "within noise") suggests may be
small, but that verdict predates the R6b planner's `within_roam`/`own_half`/race-check machinery
entirely and is not assumed to transfer (this is precisely why the analyst re-queued it). Watch
for: (a) whether the tighter roam measurably reduces long, exposed treks to the map's far edge
(a plausible mechanism for the late-throughput-ceiling documented in HANDOFF.md — shorter
average travel per fell could raise sustained throughput) without starving the chopper on sparse
maps where few trees exist within the new, smaller radius; (b) whether the anti-starvation
fallback (band 30, unaffected in structure by this change) picks up the slack cleanly on maps
where it now has to reach further/enemy-side trees more often, or whether that introduces new
exposure to the opponent's denial/production race; (c) whether this candidate closes any part of
the gap the `v1.39.0-sharepen4` sweep left unmeasured (that candidate converged at parity with
its bracket, 17.6 == 17.6, in a room the analyst flagged as possibly drift-depressed 2-3pts below
its 19.3-20.1 high-water mark — re-baseline against a fresh champion read near 19-20 before
judging this candidate's arena delta, same caveat the sharepen4 analyst left standing).
