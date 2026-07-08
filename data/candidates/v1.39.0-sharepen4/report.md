# Candidate v1.39.0-sharepen4 — Builder Report

**Task:** A one-const sweep of the proven race-check mechanism: `RACE_SHARE_PEN` 2 -> 4 (discount
joinable contested trees harder). Motivation (per task brief / analyst context): the analyst found
our worst losses show excessive trekking to contested trees, and the race check is the one
mechanism that just gained +1.3 in the arena — this is queue #1 off analyst commit `b62c977`.
Bundled with a required revert: v1.38.0-deny1's `DENY_W` probe goes back to 0 — the analyst
measured that candidate at ~17.0 (down from the 19.9-20.1 race-check band) and diagnosed a
collision with the race check's own tie-breaking. Builder role only.

**Worktree state (pre-task, resolved):** `git log --oneline -1` showed `fa33b21` ("feat: sim
Bronze support + tuned wood economy (v0.6.1)") — stale, well behind the required `2841187`.
Verified `fa33b21` is a strict ancestor of `session-2026-07-01`'s tip via `git merge-base
--is-ancestor fa33b21 session-2026-07-01` (exit 0), confirmed a clean working tree (`git status`:
nothing to commit), then fast-forwarded with `git merge --ff-only session-2026-07-01` (no rebase,
no history rewrite). Landed on `b62c977` ("analysis(census): race champion census BLOCKED by live
deny1 candidate; loss decode + queue re-rank"), which is a strict descendant of `2841187` (verified
via `git merge-base --is-ancestor 2841187 HEAD`, exit 0) — the tip of `session-2026-07-01` at task
start. This already includes v1.38.0-deny1's shipped/live state (`DENY_W=1` in the tree, as the
brief's CRITICAL BASE NOTE warned), so this candidate is the revert-plus-sweep stacked directly on
top, with no intervening drift.

## What changed

Both edits live entirely in `rust/src/botmain/planner.rs`'s `candidates()` value bands (module
consts, not touching any logic). `rust/src/botmain.rs`: `VERSION` -> `"1.39.0-sharepen4"` only.

### DENY_W: 1 -> 0 (A2 revert)

```rust
// v1.39.0-sharepen4: REVERTED — analyst b62c977 measured this candidate at ~17.0 (down from
// the 19.9-20.1 race-check band) and diagnosed a collision with the race check's own
// tie-breaking. Parked at 0 (byte-identical to pre-probe) pending a retest that doesn't fight
// RACE_SHARE_PEN; see tests/deny_probe.rs (its one test now requires DENY_W=1 and is ignored).
const DENY_W: i64 = 0; // A2 reverted — collided with the race check per analyst b62c977; knob kept at 0
```

At `DENY_W=0` the `deny_pen` term (`DENY_W * (manhattan(pc, plan.opp) as i64 / 2)`) is `0 * x == 0`
for every candidate, so every band-70/72 fell value reduces algebraically to exactly the
pre-A2-probe expression — confirmed empirically this time (unlike the deny1 builder report, which
reasoned this algebraically without a rebuild): running `tests/deny_probe.rs`'s
`tied_eta_prefers_the_contested_tree` against the `DENY_W=0` tree fails with the exact pre-probe
symptom (see TDD section below), proving the revert restores the old tie-break behavior.

### RACE_SHARE_PEN: 2 -> 4 (the sweep)

```rust
// v1.36.0-race: mild discount for a JOINABLE contested tree (an enemy is already chopping it,
// but we can arrive before they finish) — the wood splits round-robin among cell-sharers
// (engine apply_chop), so a shared tree is worth slightly less than an uncontested one, but
// never enough to lose to a materially worse alternative. « BAND, like STICKY.
// v1.39.0-sharepen4: sweep 2 -> 4 per analyst (queue #1, b62c977) — the race check is the one
// mechanism that just gained +1.3 in the arena; the analyst's decoded losses show excessive
// trekking to contested trees when a free tree is only marginally farther away, so discount
// joinable contests harder.
const RACE_SHARE_PEN: i64 = 4; // sweep 2->4 per analyst; harder discount on joinable contests
```

This is the *only* line whose wired-in effect changed: `race()`'s `Some(RACE_SHARE_PEN)` return
(the "joinable, discount it" branch) is now a bigger subtraction in the band-70/72 `ChopHere`/
`MoveTo` values. The `race()` function itself, its doomed/None branch, and all its call sites
(bands 72/70, 42/40, 31/30) are untouched — only the constant's value moved.

## TDD

### 1. RED (deny_probe, confirming the revert's semantics before parking it)

Ran `cargo test --release --test deny_probe` on the tree with `DENY_W` already flipped to `0`
(before touching the test file). Confirmed FAILING exactly as expected — the near-tie between
`(2,1)` (deep) and `(3,2)` (contested) is now a real tie again (`deny_pen=0` for both), so the
canonical `sort_by_key(|c| (-c.value, c.target))` tie-break picks the lexicographically-smaller
target `(2,1)`, not the contested `(3,2)` the test (written for `DENY_W=1`) requires:
```
thread 'tied_eta_prefers_the_contested_tree' panicked at tests/deny_probe.rs:108:5:
assertion `left == right` failed: chopper should prefer the contested tree (3,2, nearer the opponent) over the deep tree (2,1): got MOVE 2 2 1
  left: "MOVE 2 2 1"
 right: "MOVE 2 3 2"
```
This is the *identical* panic message the v1.38.0-deny1 builder report recorded pre-implementation
(`DENY_W=1` didn't exist yet then either) — confirms the revert is byte-for-byte the old behavior,
not a new bug. Marked `#[ignore]` immediately after (comment: `A2 reverted; DENY_W parked at 0
(analyst b62c977) — this assertion requires DENY_W=1`), per the brief.

### 2. RED then GREEN — `rust/tests/race_check.rs`, `share_pen_shifts_near_tie_to_free_tree`

Design (worked out against the exact `candidates()` formula, `DENY_W=0` so `deny_pen=0` for both
trees): a WINNABLE contested tree (enemy standing on it with health 4 left, chop_power 2 -> 2 turns
to fell — winnable since our chopper's `eta=1 < 2`) at map-distance 1, and a FREE tree of the same
size (so identical `chop_t=2`) at map-distance 4. Our chopper is deliberately slowed to
`movement_speed=1` (struct-update over the file's `chopper()` helper) so the small 8x5 test grid's
map-distances (1 vs 4) map directly to etas 1 vs 4 without needing an oversized grid. Band-70
`MoveTo` values reduce to `70*BAND - (steps + chop_t) - race_pen`:
- contested: `70*BAND - (1+2) - pen` = `70*BAND - 3 - pen`
- free: `70*BAND - (4+2) - 0` = `70*BAND - 6`

At `pen=2`: contested = `70*BAND-5` > free = `70*BAND-6` -> **contested wins by 1** (excessive
trekking past the free tree for a merely-discounted shared one — the losing pattern named in the
task). At `pen=4`: contested = `70*BAND-7` < free = `70*BAND-6` -> **free wins by 1**.

Confirmed RED first, with the *new test added but `RACE_SHARE_PEN` still at 2*
(`cargo test --release --test race_check`):
```
test share_pen_shifts_near_tie_to_free_tree ... FAILED
thread 'share_pen_shifts_near_tie_to_free_tree' panicked at tests/race_check.rs:140:5:
RACE_SHARE_PEN=4 should discount the joinable contest enough to prefer the free tree at (3,4): got MOVE 5 2 2
test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```
(temporarily reverted `RACE_SHARE_PEN` to `2` via `sed`, ran, confirmed the exact predicted failure
mode — contested tree `(2,2)` chosen instead of free `(3,4)` — then restored to `4`.)

Confirmed GREEN after restoring `RACE_SHARE_PEN = 4`:
```
test share_pen_shifts_near_tie_to_free_tree ... ok
test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Gate results

1. **Baseline** (tree as landed, `DENY_W=1`/`RACE_SHARE_PEN=2`, before any edit): **27 suites**
   (15 empty unittest bins + 11 integration test files + 1 doctest), 52 passed + 4 ignored (the
   T-hand-parked ignores in `tactics_scale.rs`) + 0 failed.
2. **RED — deny_probe** (after `DENY_W: 1 -> 0` only): 1 FAILED, exact message quoted above.
3. **RED — race_check** (after adding the new test, `RACE_SHARE_PEN` still `2`): 1 FAILED (2
   passed + 1 failed), exact message quoted above.
4. **cargo build --release** (post all edits): clean — the same 5 pre-existing warnings as the
   deny1 baseline (`PLUM` unused import in `printer_bot.rs`, `opp` unused var in `boss_v3.rs`,
   `HARVESTER` dead-code x2 in `silver_boss.rs`/`mybot.rs`, `Strategy` unused import in
   `fastcheck.rs`) plus one **pre-existing** `starter` dead-code warning in `tests/race_check.rs`
   (confirmed present in the unmodified baseline log too — `starter()` was already unused by the
   file's first two tests; my new test uses `chopper()` + a struct-update, not `starter()`, so this
   is unchanged, not introduced). **No new warnings.**
5. **GREEN — cargo test --release** (post all edits): **27 suites**, all green.
   `race_check`: **3 passed** (gained `share_pen_shifts_near_tie_to_free_tree`).
   `deny_probe`: **0 passed, 1 ignored** (lost its pass, now ignored per the brief).
   Every other suite unchanged: `motion_corridor` 2, `nanaflow` 2, `phase_factory` 1, `phase_hoard`
   7, `phase_skeleton` 2, `planner_solver` 3, `planner_tasks` 3, `sim_engine_tests` 26,
   `tactics_scale` 3 passed + 4 ignored (T-hand, untouched). **Total: 52 passed + 5 ignored + 0
   failed across 27 suites.** (Net passed count unchanged at 52: -1 from `deny_probe`, +1 from
   `race_check`; ignored count +1, from 4 to 5.)
6. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8 300
   target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
7. **tools/bundle.py**: `src/botmain.rs -> target/refactor/bundled.rs: 74443 chars`. Grep confirms
   `VERSION: &str = "1.39.0-sharepen4"`, `const DENY_W: i64 = 0;`, `const RACE_SHARE_PEN: i64 = 4;`,
   and exactly 3 occurrences of `deny_pen` (1 definition + 2 uses, both inside the 70/72 block —
   the wiring is untouched from v1.38.0-deny1, only the constant's value changed).
8. **rustc --edition 2021 -O** on the bundled source (dot-free copy): exit 0 (SRC-COMPILE-OK).
9. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8 seeds x
   2 seats), all command streams identical`.
10. **tools/minify.py**: `74443 -> 43653 chars (58%)` — 56% under the 100,000 B cap.
11. **rustc --edition 2021 -O** on the minified copy (dot-free copy): exit 0 (MIN-COMPILE-OK).
12. **Minified bin vs target/release/bot**: `EQUAL: 16 games (8 seeds x 2 seats), all command
    streams identical`.
13. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the frozen
    bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Minified: `74442 -> 43652 chars
    (58%)` (1 byte shorter than the release `.min.rs` because `false`->`true` is one character
    shorter). `rustc --edition 2021 -O` compile-check: exit 0 (DBG-COMPILE-OK). 2-seed local smoke:
    `./target/release/equality <probe> target/release/bot 2 300 target/release/bot` -> `EQUAL: 4
    games (2 seeds x 2 seats), all command streams identical` (no crash; DEBUG only echoes to
    stderr, so stdout-parity holds).
14. **Champion-equality: N/A by design**, same reasoning as v1.38.0-deny1 — this candidate
    intentionally changes behavior (both the `DENY_W` revert and the `RACE_SHARE_PEN` sweep alter
    ranking outcomes in specific contested/near-tie scenarios by construction; see the TDD section).
    Self-determinism (gate 6) and the bundle/minify round-trip equalities (gates 9, 12) confirm the
    change is fully deterministic and shuffle-invariant in self-play, which is a different, weaker
    guarantee than champion-equality and is not conflated with it here.

## Sizes

- `cgauto/submissions/v1.39.0-sharepen4.rs`: **75,820 B** (bundled, comments retained).
- `cgauto/submissions/v1.39.0-sharepen4.min.rs`: **43,653 B** (56% under the 100,000 B cap).
- `data/candidates/v1.39.0-sharepen4/v1.39.0-sharepen4.rs` / `.min.rs`: byte-identical (`cmp`
  -verified) to the `cgauto/submissions/` copies above.
- `data/candidates/v1.39.0-sharepen4/v1.39.0-sharepen4.debug-probe.min.rs`: **43,652 B** (DEBUG=true;
  1 byte shorter than the release `.min.rs`).

## Diffstat

```
rust/src/botmain.rs         |  2 +-   (VERSION only)
rust/src/botmain/planner.rs | 12 ++++++++++--  (DENY_W 1->0, RACE_SHARE_PEN 2->4, comments)
rust/tests/deny_probe.rs    |  3 +++  (#[ignore] + comment on the one test)
rust/tests/race_check.rs    | 32 ++++++++++++++++++++++++++++++++  (new test)
4 files changed, 46 insertions(+), 3 deletions(-)
```

## Scope discipline

Only the two named constants (`DENY_W`, `RACE_SHARE_PEN`) and `VERSION` were touched, plus the
`#[ignore]` annotation on the one test whose assertion is definitionally incompatible with
`DENY_W=0`. NOT touched: the `race()` helper's logic and its doomed/None branch, the anti-
starvation fallback (30/31), the starter's chop-help band (40/42), funding bands
(60/58/65/64/63/45/44), the printer/tree-first bands (52/50/49) and diagonal plant-placement
geometry from v1.37.0-nanaflow, `seed_cells`/`fell_ok`'s protection logic, `STICKY`,
`GE_MAX_TROLLS`/training/`tactics.rs`, or `motion.rs`.

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` then vs field (incl. >=1 denial-style
opponent — mikdiet 6480914 / plcc 6480966 — and >=1 >=19.6 player per `field_targets.py`). Read
`cgauto/ramp.py --last 8` (wood >=45, t300 delta vs -15.3 baseline) and telemetry from the newest
`.raw` files (`@TFFARM` / `@TFPHASE`). Expected signature: this is a pure re-tuning of an already-
proven mechanism (the race check itself is unchanged in structure), so the effect should be
concentrated specifically in games with overlapping chop zones / contested trees — sparse maps or
maps where territories never overlap should show ~zero effect (same "only breaks near-ties, never
overrides the priority hierarchy" guarantee `RACE_SHARE_PEN` has always carried, just amplified).
Watch for: (a) whether harder discounting of joinable contests reduces the "excessive trekking to
contested trees" loss pattern the analyst flagged, without introducing a new failure mode (e.g.
abandoning genuinely winnable contests that were previously correctly joined — the anti-
starvation/other bands' independent `race_pen` uses at bands 42/40/31/30 are unaffected by this
constant change in *structure*, but ARE affected in *magnitude* since they share the same
`RACE_SHARE_PEN` constant — this candidate does NOT scope the sweep to bands 70/72 only, unlike
v1.38.0-deny1's `DENY_W` which was band-70/72-scoped by construction); (b) the `DENY_W` revert
should return denial/contested-tree targeting to the exact pre-v1.38.0-deny1 baseline (confirmed
structurally via the deny_probe RED-with-old-symptom match above) — no denial-side regression is
expected or possible from this half of the change; (c) whether the sweep measurably closes any of
the late-throughput-ceiling gap documented in HANDOFF.md, or whether `RACE_SHARE_PEN=4` is
overshooting (a follow-up sweep at an intermediate value, e.g. 3, may be needed if this candidate
under- or over-shoots).

## Arena verdict (arena-runner, final — 2026-07-08 03:37) — KEEP, AT PARITY

Boss/field gate was waived per the queue-never-idles policy (arena-runner brief went straight
from champion-reconvergence to submit; no separate gatekeeper episode ran for this candidate).

**Bracket** (champion v1.36.0-race reconvergence after the deny1 revert, independently
re-confirmed): 3 consecutive `cg_rank.py` reads 02:28/02:37/02:47 all **121/527 @ 17.6**
(agentId 6542647; matches the deny1 runner's own closing record exactly). BRACKET = 17.6.

**Submit**: 02:47:19, `api_submit.py cgauto/submissions/v1.39.0-sharepen4.min.rs` →
`TestSession/submit: 200 40965544` → SUBMIT-OK.

**Convergence** (agentId 6542656 confirmed live throughout):

| time (MSK) | Δt post-submit | rank | score |
|---|---|---|---|
| 03:07:11 | +20m | 123/527 | 17.4 |
| 03:22:16 | +35m | 121/527 | 17.6 |
| 03:37:26 | +50m | 121/527 | 17.6 |

Flat from +20m, converged 121/527 @ 17.6 by +35m (unchanged at +50m, 15m5s apart, Δ0.0) — not
ambiguous, decided at +50m, no +65m read needed.

**Verdict:** converged 17.6 == bracket 17.6 exactly (≥ bracket−0.2 = 17.4) → **KEEP**. The
`RACE_SHARE_PEN` 2→4 sweep (with `DENY_W` parked at 0) produced no measurable change vs the
champion's own immediately-preceding reconvergence reading in this arena room — a clean tie.
Candidate remains the live arena entry; no revert performed.

**Phase 4 (parity rule):** `cgauto/api_submit.py` default left unchanged at
`v1.36.0-race.min.rs` — sharepen4 is kept live but NOT promoted to champion/default status
(mirrors the v1.28.3-sticky6 NEUTRAL precedent).

**Goal gate (rank ≤99):** did not fire (all reads 117-123 this episode).

**For the analyst:** the sweep is a null result in this room at this moment — cannot
distinguish "mechanism already saturated at RACE_SHARE_PEN=2" from "effect masked by the
~2pt night-drift band currently depressing the champion itself (19.3-20.1 -> 17.6)". Queue
#2 (chop_r 5→4) is unaffected by this result and remains the correct next submit; re-baseline
against a fresh champion read near 19-20 before judging future small-delta sweeps in this
room. Full read sequence and reasoning: `docs/silver-experiment-log.md`, "## v1.39.0-sharepen4
arena verdict (2026-07-08 03:37)".
