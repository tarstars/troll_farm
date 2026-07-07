# Candidate v1.38.0-deny1 — Builder Report

**Task:** Track A's denial-weight probe (A2): bias the chopper's PRIMARY fell choice (bands
70/72 only) toward CONTESTED trees — those nearer the opponent — so shared-map wood is taken
before the enemy can get it. Historical basis: denial weighting toward the foe's shack
(`MB_DENIAL_W` in the pre-planner `botmain.rs` deciders) was the single biggest lever of the
silver era; the R6b joint planner (`planner.rs`) has carried weight 0 since it replaced that
sequential cascade. Builder role only. Champion-equality gate explicitly waived per the brief
("NO champion-equality (behavior change)") — this candidate is a deliberate behavior change,
not a refactor.

**Worktree state (pre-task, resolved):** `git log --oneline -1` showed `fa33b21` ("feat: sim
Bronze support + tuned wood economy (v0.6.1)") — stale, well behind the required `92324e7`.
Verified `fa33b21` is a strict ancestor of `session-2026-07-01`'s tip via `git merge-base
--is-ancestor fa33b21 92324e7` (exit 0), confirmed a clean working tree, then fast-forwarded
with `git merge --ff-only session-2026-07-01` (no rebase, no history rewrite). Landed exactly
on `92324e7` ("Merge branch 'worktree-agent-a398743af04627249' into session-2026-07-01"), the
commit named in the brief — this already includes v1.37.0-nanaflow's shipped state (`git diff
--stat` against the starting tree touched only this candidate's own files: `rust/src/botmain.rs`,
`rust/src/botmain/planner.rs`, plus the new `rust/tests/deny_probe.rs`), so this candidate
stacks directly on nanaflow with no intervening drift.

## What changed

Both edits live entirely in `rust/src/botmain/planner.rs`'s `candidates()` (the L2 joint
task-assignment value bands), scoped to the chopper's PRIMARY fell loop only. `rust/src/botmain.rs`:
`VERSION` → `"1.38.0-deny1"` only.

### New constant (near `STICKY`)

```rust
// v1.38.0-deny1 (A2 probe): bias the PRIMARY fell choice (bands 70/72 ONLY — not the
// anti-starvation fallback, not the starter's chop-help band) toward trees nearer the
// opponent's shack. Silver-era denial weighting toward the foe was the single biggest lever
// measured pre-planner (MB_DENIAL_W in botmain.rs); the R6b joint planner has carried weight
// 0 since it replaced that cascade. At DENY_W=0 every fell value is byte-identical to the
// pre-probe code (the subtracted term is `0 * x == 0`); DENY_W=1 only breaks near-ties and
// nudges marginal calls, « BAND — never overrides the priority hierarchy.
const DENY_W: i64 = 1; // A2 probe: prefer contested trees (0 = off; silver-era denial was the biggest lever)
```

### Wired into the chopper's primary fell loop ONLY (bands 70/72)

```rust
let race_pen = match race(pc, steps) {
    None => continue,
    Some(pen) => pen,
};
// A2 probe (DENY_W): trees closer to the opponent lose less -> rank higher.
let deny_pen = DENY_W * (manhattan(pc, plan.opp) as i64 / 2);
if pc == u.pos() {
    out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 72 * BAND - chop_t - race_pen - deny_pen });
} else {
    out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen });
}
```

**Scope discipline (per brief: "band-70/72 fell values ONLY"):** the chopper's anti-starvation
fallback (bands 30/31, `p.size >= 1`, right after this loop) and the starter's chop-help bands
(40/42) plus ITS anti-starvation duplicate (30/31) are all untouched — confirmed by grep (the
bundle below shows exactly one `deny_pen` definition and two uses, both inside the 70/72
block; `git diff` confirms no other lines moved).

**Byte-identical at DENY_W=0 (reasoning, not measured — DENY_W is compiled to `1` in this
candidate so there is no runtime flag to flip):** `deny_pen = DENY_W * (manhattan(pc, plan.opp)
as i64 / 2)`. With `DENY_W = 0`, this is `0 * x == 0` for every `x`, so `value: N*BAND - … -
deny_pen` reduces algebraically to exactly the pre-probe expression `N*BAND - …` — the same
`i64` arithmetic, so no test, band, or ranking changes at DENY_W=0. This is a reasoned claim
(no A/B rebuild performed, since the brief runs this candidate at DENY_W=1 only), noted per
the brief's instruction.

## TDD

### 1. RED — `rust/tests/deny_probe.rs`, `tied_eta_prefers_the_contested_tree`

Two equal-size (size-2, health-4) fellable bananas, both in OUR half (`own_half`: manhattan to
our shack `(0,2)` <= manhattan to opp shack `(7,2)`) and both within farm/roam radius:
- `(2,1)` — deep in our half: manhattan-to-shack 3, manhattan-to-opp 6 (own_half OK).
- `(3,2)` — toward the contested middle: manhattan-to-shack 3, manhattan-to-opp 4 (own_half OK,
  but only just).

Chopper (`ms=2, cc=2, hp=0, chop=2`, `id=2`) at `(2,3)`. The 8x5 room has only `(0,2)` removed
from `walkable` (the shack cell), and neither target is near `x=0`, so BFS map-distance equals
Manhattan distance here: dist to `(2,1)` = 2, dist to `(3,2)` = 2 -- a genuine tie (`eta`=1 for
both at ms=2). Both trees are size-2 (`chop_t`=2 for both, chop_power=2) and no enemy troll
occupies either cell (`race_pen`=0 for both). Every term the pre-fix formula
(`70*BAND - steps - chop_t - race_pen`) used is IDENTICAL for both trees -- a real tie, not a
coincidence. Pre-fix, `sort_by_key(|c| (-c.value, c.target))` breaks the tie lexicographically:
`Some((2,1)) < Some((3,2))`, so the deep tree wins.

Confirmed FAILING pre-implementation (`cargo test --release --test deny_probe`):
```
thread 'tied_eta_prefers_the_contested_tree' panicked at tests/deny_probe.rs:108:5:
assertion `left == right` failed: chopper should prefer the contested tree (3,2, nearer the opponent) over the deep tree (2,1): got MOVE 2 2 1
  left: "MOVE 2 2 1"
 right: "MOVE 2 3 2"
```
This exactly matches the brief's predicted pre-fix behavior ("(2,1) < (3,2) wins").

### 2. GREEN -- post-implementation

`deny_pen((2,1)) = 1 * (manhattan((2,1),(7,2)) / 2) = 1 * (6/2) = 3` -> value `70*BAND - 6`.
`deny_pen((3,2)) = 1 * (manhattan((3,2),(7,2)) / 2) = 1 * (4/2) = 2` -> value `70*BAND - 5`.
`(3,2)` now wins OUTRIGHT (`70*BAND-5 > 70*BAND-6`, a strict inequality -- not a tie-break
artifact). Test passes: `cmds[&2] == "MOVE 2 3 2"`.

## Gate results

1. **Baseline** (inherited from v1.37.0-nanaflow, no rust/ drift on this worktree -- see
   above): 26 suites (15 empty unittest bins + 10 integration test files + 1 doctest), 51
   passed + 4 ignored + 0 failed.
2. **RED**: `cargo test --release --test deny_probe` on the unmodified tree -> 1 FAILED, exact
   message quoted above.
3. **cargo build --release** (post-change, forced full rebuild via `touch src/botmain.rs`):
   clean -- exactly the same 5 pre-existing warnings as nanaflow's baseline (`PLUM` unused
   import in `printer_bot.rs`, `opp` unused var in `boss_v3.rs`, `HARVESTER` dead-code x2 in
   `silver_boss.rs`/`mybot.rs`, `Strategy` unused import in `fastcheck.rs`) -- **no new
   warnings**.
4. **GREEN -- cargo test --release** (post-change): **27 suites**, all green. New
   `deny_probe.rs`: 1 passed. Every pre-existing suite unchanged: `motion_corridor` 2,
   `nanaflow` 2, `phase_factory` 1, `phase_hoard` 7, `phase_skeleton` 2, `planner_solver` 3,
   `planner_tasks` 3, `race_check` 2, `sim_engine_tests` 26, `tactics_scale` 3 passed + **4
   ignored** (the T-hand-parked ignores, untouched by this candidate -- confirmed still
   `#[ignore]`). **Total: 52 passed + 4 ignored + 0 failed across 27 suites.**
5. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8
   300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams
   identical`.
6. **tools/bundle.py**: `src/botmain.rs -> target/refactor/bundled.rs: 73696 chars`. Grep
   confirms `VERSION: &str = "1.38.0-deny1"`, `const DENY_W: i64 = 1;` (defined once, used
   from exactly 2 sites -- the ChopHere/MoveTo pushes inside the 70/72 block -- confirming the
   "one helper, narrow scope" design), and the untouched `const RACE_SHARE_PEN: i64 = 2;`
   from v1.36.0-race (present verbatim).
7. **rustc --edition 2021 -O** on the bundled source (dot-free copy): exit 0
   (SRC-COMPILE-OK).
8. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` -> `EQUAL: 16 games (8
   seeds x 2 seats), all command streams identical`.
9. **tools/minify.py**: `73696 -> 43649 chars (59%)` -- 56% under the 100,000 B cap.
10. **rustc --edition 2021 -O** on the minified copy (dot-free copy): exit 0
    (MIN-COMPILE-OK).
11. **Minified bin vs target/release/bot**: `EQUAL: 16 games (8 seeds x 2 seats), all
    command streams identical`.
12. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Minified: `73695 ->
    43648 chars (59%)`. `rustc --edition 2021 -O` compile-check: exit 0 (DBG-COMPILE-OK).
    2-seed local smoke: `./target/release/equality <probe> target/release/bot 2 300
    target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical` (no crash; DEBUG only echoes to stderr, so stdout-parity holds).
13. **Champion-equality: N/A by design** (per brief) -- not run against
    `cgauto/submissions/v1.28.3-sticky6.min.rs`. This candidate intentionally changes
    behavior: any time two fellable trees in our half are near-tied on ETA/chop-time, the one
    closer to the opponent now ranks higher (a strict inequality, not merely a tie-break
    flip, whenever `manhattan(pc, opp)` differs between candidates). Self-determinism (gate
    5) and the bundle/minify round-trip equalities (gates 8, 11) confirm the change is fully
    deterministic and shuffle-invariant in self-play; that is a different, weaker guarantee
    than champion-equality and is not conflated with it here.

## Sizes

- `cgauto/submissions/v1.38.0-deny1.rs`: **75,067 B** (bundled, comments retained).
- `cgauto/submissions/v1.38.0-deny1.min.rs`: **43,649 B** (56% under the 100,000 B cap).
- `data/candidates/v1.38.0-deny1/v1.38.0-deny1.rs` / `.min.rs`: byte-identical (`cmp`-verified)
  to the `cgauto/submissions/` copies above.
- `data/candidates/v1.38.0-deny1/v1.38.0-deny1.debug-probe.min.rs`: **43,648 B** (DEBUG=true;
  1 byte shorter than the release `.min.rs` because `false`->`true` is one character shorter).

## Diffstat

```
rust/src/botmain.rs         |  2 +-   (VERSION only)
rust/src/botmain/planner.rs | 14 ++++++++++++--  (DENY_W const + 2 wire-up sites, bands 70/72 only)
rust/tests/deny_probe.rs    | new file, 113 lines, 1 test
```

## Scope discipline

Only the named mechanism (bands 70/72, the chopper's PRIMARY fell choice) was touched. NOT
touched: the anti-starvation fallback (30/31, both copies), the starter's chop-help band
(40/42), the v1.36.0-race `race()` helper and `RACE_SHARE_PEN` (present verbatim, untouched),
funding bands (60/58/65/64/63/45/44), the printer/tree-first bands (52/50/49) and diagonal
plant-placement geometry from v1.37.0-nanaflow (untouched), `seed_cells`/`fell_ok`'s
protection logic, `GE_MAX_TROLLS`/training/`tactics.rs`, or `motion.rs`.

## Arena verdict (arena-runner, 2026-07-08) — REVERT

**Bracket** 00:46:06: rank 111/527, Gold score 19.3, agentId=6542604. **Submit** 00:46:19-22:
`api_submit.py cgauto/submissions/v1.38.0-deny1.min.rs` → SUBMIT-OK (TestSession 40965251).

**Convergence** (agentId 6542627, stable across all three):

| time | Δt | rank | score |
|---|---|---|---|
| 01:06:54 | +20m | 146/527 | 16.5 |
| 01:21:39 | +35m | 141/527 | 16.8 |
| 01:36:35 | +50m | 135/527 | 17.0 |

Converged ~17.0 vs bracket 19.3 (need ≥19.1 to KEEP) — a clear −2.3pt regression, decisively
below the keep bar. Independently corroborated by the analyst's parallel `battles.py`/loss-
replay census (`b62c977`), which measured the identical 17.0/~135 convergence point by a
different method, and diagnosed the mechanism: `DENY_W`'s bands-70/72 tie-break collides with
`race()`'s doomed-target check at the same decision point, producing excessive travel (worst-loss
MOVE:CHOP ratio 1.5-2.6x the ~2.7 historical baseline in 2/3 decoded replays).

**Process note:** a parallel "controller" process, believing this runner had gone silent past its
decision window (it had not — it was mid-flight on the brief's own explicitly-allowed +65m
confirmatory read, a normal 60-65 minute mark for this brief), independently resubmitted
`v1.36.0-race.min.rs` at 01:47:07 before this runner's own +65m read landed. That read (01:51:22,
353/527 @ 12.0, agentId=6542647) is therefore the *freshly resubmitted champion's* own cold-start
noise, not a deny1 data point — discarded. The uncontaminated +20/+35/+50 trajectory above is
sufficient on its own to decide REVERT, and matches the controller's and analyst's independent
conclusions exactly (unanimous three ways, coordination gap only).

**Champion reconvergence** (verifying the already-executed revert; agentId 6542647 throughout):

| time | Δt post-resubmit | rank | score |
|---|---|---|---|
| 01:51:22 | +4m | 353/527 | 12.0 |
| 02:07:18 | +20m | 117/527 | 17.9 |
| 02:22:14 | +35m | 121/527 | 17.6 |
| 02:37:14 | +50m | 121/527 | 17.6 |

Two stable reads (+35m/+50m, 121/527 @ 17.6, Δ0.0) satisfy the reconvergence bar. Level sits
below the champion's most recent 19.3 mark but is byte-identical code (api_submit.py default
unchanged) — consistent with this room's documented score drift, not a code regression. Arena
NOT left on a regressed bot.

**Goal gate (rank ≤99):** did not fire on any read this episode.

**VERDICT: REVERT.** No `api_submit.py` default change (already pointed at v1.36.0-race.min.rs).
Full detail, including the process-collision note, in `docs/silver-experiment-log.md`
("## v1.38.0-deny1 arena verdict") and `docs/arena-queue.md`.

## Next steps (gatekeeper)

`collect_debug_games.py <debug-probe.min.rs> boss 8` then vs field (incl. >=1 denial-style
opponent -- mikdiet 6480914 / plcc 6480966 -- and >=1 >=19.6 player per `field_targets.py`).
Expected signature: this is the FIRST planner-era reintroduction of denial weighting, so
watch specifically for (a) contested-tree win-rate / wood-race outcomes shifting versus the
current champion on maps with overlapping chop zones (the mechanism only ever changes
anything when two fellable trees are near-tied AND differ in distance-to-opponent -- sparse or
non-adjacent-territory maps should show ~zero effect); (b) no regression in `ramp.py --last
8` wood/delta numbers on maps where chop zones never overlap (this is a targeting reorder, not
an economy/training change -- `DENY_W`'s `« BAND` scale means it can only break near-ties or
nudge marginal calls, never override the priority hierarchy); (c) whether the denial bias
measurably improves the late-throughput-ceiling documented in HANDOFF.md -- historically
denial weighting was the single biggest lever pre-planner, so this is the natural first place
to look for arena movement, but the effect size at `DENY_W=1` (« BAND) is deliberately small
and may need a follow-up sweep (`DENY_W=2,3,...`) if this first slice under-moves the needle.
