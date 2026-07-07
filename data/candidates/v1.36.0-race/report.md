# Candidate v1.36.0-race — Builder Report

**Task:** DOOMED-TARGET RACE CHECK + split-aware contest joining in fell valuation (user
replay finding #1, spec Amendment 2). Builder role only; champion-equality gate explicitly
waived per the brief (behavior changes by design — but ONLY in enemy-contested situations,
see "Champion-equality" below). Base tree: fast-forwarded to session-2026-07-01 tip 3283d55
("queue(user-findings): race-check, banana tree-first flow, diagonal farm geometry — spec
Amendment 2"), which sits on top of 99fb7dc (T-hand gatekeeper verdict #3: PASS).

**Worktree anomaly (pre-task, resolved):** this worktree was checked out 178 commits behind,
at `fa33b21` — a pre-Rust, Bronze-era Python commit (no `rust/`, `cgauto/`, `tools/`, or
`data/` directories existed). Verified `fa33b21` is a strict ancestor of the current
`session-2026-07-01` tip (`git merge-base --is-ancestor` exit 0) and that the worktree had a
clean status, then fast-forwarded (`git merge --ff-only session-2026-07-01`, no rebase, no
history rewrite, zero risk of losing work) before starting any task work. Two sibling
worktrees inspected for comparison were similarly stale (old RHEA/RL branches), so this
appears to be a general staleness issue with pre-existing `.claude/worktrees/*` directories,
not something specific to this task.

## What changed

### 1. Base reconfig (stack on champion config, one variable at a time)
- `rust/src/botmain.rs`: `GE_MAX_TROLLS` 3 -> 2 (T-hand parked pending its arena verdict;
  comment: "re-arm by setting 3"). `VERSION` -> `"1.36.0-race"`. `GE_FEEDER_T=45` and
  `GE_FEEDER_FARM=0` left untouched (inert at MAX=2, per brief) — all T-hand funding-band
  machinery (`ladder_funding`, the 65/64/63 bands) stays in place in `planner.rs`, just
  unreachable again since `want_feeder` requires `n < GE_MAX_TROLLS` which is now `n < 2`.

### 2. Tests parked by the reconfig (tactics_scale.rs)
Reverting `GE_MAX_TROLLS` to 2 makes `want_feeder` permanently false for any test built on
`n=2` (starter+chopper) trolls, since `nchop>=1 && n<GE_MAX_TROLLS` becomes `1>=1 && 2<2` =
false. **All 4** T-hand-era tests that assert `want_feeder==true` under this construction
fail identically (verified empirically pre-ignore: `cargo test --release --test
tactics_scale` -> 4 FAILED, all `left: false, right: true` on the `want_feeder` assertion):
`tempo_wants_third_hand`, `tempo_wants_third_hand_farm3`, `tempo_hand_iron_funding_after_chopper`,
`tempo_wants_third_hand_dead_farm`. (The brief's parenthetical said "3 tests" — the
`tempo_wants_third_hand*` glob alone already matches 3 of these; the actual failing set is 4.
Applied the brief's specified `#[ignore]` route to all 4 that actually regress, not just 3,
since the stated goal is "make sure everything else is green" and a partial fix would leave
1 test red.) Each gets: `#[ignore]` + a one-line comment "parked with T-hand; re-enable when
GE_MAX_TROLLS≥3" directly above `#[test]`. `scale_hoard_plan`/`scale_factory_plan`/
`tempo_plan_matches_tempo_semantics` (Meta::Scale or n=1 constructions) are unaffected and
stay green — confirmed by inspection (Scale's ladder path never reads `GE_MAX_TROLLS`; it has
its own `SCALE_MIN_TURN`/`n<4` gate) and by the test run.

### 3. The race check (rust/src/botmain/planner.rs)
New const near `STICKY`:
```rust
const RACE_SHARE_PEN: i64 = 2; // « BAND, like STICKY
```
New closure in `candidates()`, defined once per call (right after `fell_ok`/`own_half`/
`within_roam`, before any candidate is pushed) and reused by every fell-type loop:
```rust
let race = |pc: Cell, our_eta: i64| -> Option<i64> {
    let occupant = state.opp_trolls.iter().find(|e| e.pos() == pc && e.chop_power > 0);
    match occupant {
        None => Some(0),
        Some(e) => {
            let h = state.trees.iter().find(|p| p.pos() == pc).map(|p| p.health).unwrap_or(0) as i64;
            let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
            if their_turns <= our_eta { None } else { Some(RACE_SHARE_PEN) }
        }
    }
};
```
Wired into all 4 fell-candidate pushes (the only ones the brief named — plant/harvest/bank/
mine/fund/printer bands are untouched): chopper primary fell (band 72/70), chopper
anti-starvation (31/30), starter chop-help (42/40), starter chop-help anti-starvation (31/30).
At each site: `steps` (the existing ETA-in-turns) is already computed; `race(pc, steps)` is
called once, `None` -> `continue` (drop the candidate before pushing either the ChopHere or
MoveTo variant), `Some(pen)` -> subtract `pen` from whichever variant's value gets pushed.

**Race-model semantics:**
- No enemy troll standing exactly on the candidate tree's cell (or one is, but with
  `chop_power == 0`, e.g. a starter): `Some(0)` — no adjustment, behaves exactly as before.
- Enemy chopper on the tree: `their_turns = ceil(tree.health / enemy.chop_power)`. Compare
  to `our_eta` (turns, `ceil(dist/our_ms)` — the same `steps` value already used in the
  value formula, i.e. turns, not raw cell distance).
  - `their_turns <= our_eta`: **doomed** — they fell it at or before we'd arrive, so walking
    there donates the travel for a tree that's gone (or shared for 0 turns) by the time we
    get there. The candidate is dropped entirely (not merely devalued) so it can never win a
    tie against a legitimate alternative, and so it can't leak into the anti-starvation
    fallback either (that loop gets the same `race()` call).
  - `their_turns > our_eta`: **joinable** — we arrive before they finish; the engine's
    `apply_chop` splits the wood round-robin among cell-sharers, so the tree is still worth
    going for, just discounted by `RACE_SHARE_PEN=2` (« BAND=100,000, so it only breaks
    near-ties against other candidates, never flips a decisively-better alternative — same
    scale discipline as `STICKY`).
- `race` is a pure function of `state` (immutable borrow only, no thread-local/mutable
  state) — called with the same inputs regardless of troll iteration order, so **shuffle
  invariance holds** (verified: self-determinism gate below).
- Scope: fell-type candidates ONLY, exactly the 4 sites named in the brief (bands 72/70,
  42/40, 31/30 x2). Plant/harvest/bank/mine/funding/printer bands are untouched.

### 4. New test file: rust/tests/race_check.rs
Helpers copied verbatim from `planner_tasks.rs` (`base_state`/`base_plan`/`starter`/
`chopper`/`banana`; `base_plan().phase == Phase::Tempo`, unchanged). Two tests:
- `doomed_contested_tree_is_skipped`: enemy `chopper(9,3,2)` stands ON tree `(3,2)`
  (health overridden to 2; enemy `chop_power=2` from the `chopper()` helper ->
  `their_turns=ceil(2/2)=1`). Our `chopper(2,1,2)` (`ms=2`) is map-distance 2 away ->
  `our_eta=ceil(2/2)=1` turn. `1<=1` -> doomed. A farther free tree at `(6,2)` (no enemy)
  must be picked instead. Asserts `cmds[&2]` contains `"6 2"` and does NOT contain `"3 2"`.
- `winnable_contest_is_joined`: same enemy troll but `chop_power` reduced to 1 and tree
  health set to 9 -> `their_turns=ceil(9/1)=9`; `our_eta=1` (same geometry) -> `9<=1` false
  -> joinable. Asserts `cmds[&2]` contains `"3 2"` (we still go for the near, winnable tree
  over the untouched, much-farther `(7,2)` distractor).

**TDD note (deviation from the brief's "both tests must FAIL first"):**
`doomed_contested_tree_is_skipped` was confirmed FAILING pre-implementation (`cargo test
--release --test race_check` -> got `MOVE 2 3 2`, i.e. walked straight into the doomed race —
this is the bug the fix targets). `winnable_contest_is_joined` was confirmed **already
passing** pre-implementation. This is structurally unavoidable, not a construction error: the
only behavioral effects the fix can ever introduce are (a) removing a doomed candidate
entirely, or (b) applying a small downward discount (`RACE_SHARE_PEN=2`) to a joinable one —
both changes can only make a contested tree LESS attractive relative to the pre-fix baseline,
never more. So no possible construction of "the winnable contest should still be joined" can
fail against code that ignores enemies entirely (that code was always going to join it, for
the wrong reason — indifference, not race-awareness). This test is a regression guard against
a future overly-aggressive implementation (e.g., one that skips any enemy-occupied tree
regardless of health/eta), not a bug demonstration; it was verified to exercise the real
`race()` logic post-implementation (the near tree's value now correctly reflects
`- RACE_SHARE_PEN`, confirmed by code inspection of the wired call site).

## Gate results

1. **Baseline** (before any change): `cargo build --release` clean (pre-existing warnings
   only); `cargo test --release`: 24 suites (15 empty unittest bins + 8 integration files +
   1 doctest), 51 tests passed, 0 failed, 0 ignored.
2. **cargo build --release** (post-change): clean, same 4 pre-existing warnings only
   (`opp` unused var, `HARVESTER` dead-code x2, `Strategy` unused import in `fastcheck.rs`)
   — no new warnings.
3. **cargo test --release** (post-change): **25 suites**, all green. `tactics_scale.rs`:
   3 passed + 4 ignored (0 failed). New `race_check.rs`: 2 passed. Every other suite
   unaffected: `motion_corridor` 2, `phase_factory` 1, `phase_hoard` 7, `phase_skeleton` 2,
   `planner_solver` 3, `planner_tasks` 3, `sim_engine_tests` 26 — all unchanged pass counts
   (verified by inspection: only `phase_hoard.rs`'s two tests that populate `opp_trolls`
   place the enemy 3+ cells from any tree cell, so `race()` never finds an occupant there;
   every other test file leaves `opp_trolls` empty). **Total: 49 passed + 4 ignored + 0
   failed across 25 suites.**
4. **Self-determinism**: `./target/release/equality target/release/bot target/release/bot 8
   300 target/release/bot` -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams
   identical`.
5. **tools/bundle.py**: `src/botmain.rs -> target/refactor/bundled.rs: 71455 chars`. Grep
   confirms `VERSION: &str = "1.36.0-race"`, `GE_MAX_TROLLS: i32 = 2` (comment: "T-hand
   parked..."), `const RACE_SHARE_PEN: i64 = 2;` (defined once, called from the 4 sites via
   `race(pc, steps)` — confirms the "one helper" design, not 4 copies).
6. **rustc --edition 2021 -O** on the bundled source (dot-free copy): exit 0
   (`SRC-COMPILE-OK`).
7. **Bundle-inlining sanity**: bundled bin vs `target/release/bot` ->
   `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
8. **tools/minify.py**: `71455 -> 43306 chars (60%)` — 57% under the 100,000 B cap.
9. **rustc --edition 2021 -O** on the minified copy (dot-free copy): exit 0
   (`MIN-COMPILE-OK`).
10. **Minified bin vs target/release/bot**: `EQUAL: 16 games (8 seeds x 2 seats), all
    command streams identical`.
11. **DEBUG probe**: `sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/'` on the
    frozen bundled `.rs` -> exactly 1 hit of `true`, 0 remaining `false`. Minified: `71454 ->
    43305 chars (60%)`. `rustc --edition 2021 -O` compile-check: exit 0 (`DBG-COMPILE-OK`).
    2-seed local smoke: `./target/release/equality <probe> target/release/bot 2 300
    target/release/bot` -> `EQUAL: 4 games (2 seeds x 2 seats), all command streams
    identical` (no crash; DEBUG only echoes to stderr, so stdout-parity holds as documented
    in prior candidates).
12. **Champion-equality: N/A by design** (per brief item 4) — NOT run against
    `cgauto/submissions/v1.28.3-sticky6.min.rs`. This candidate intentionally changes
    behavior, but narrowly: only when an enemy troll physically occupies a cell that is also
    one of our own fell candidates (a contested tree) — everywhere else the value formula is
    byte-for-byte the same arithmetic as before (`race()` returns `Some(0)` whenever no such
    occupant exists, a no-op add). The two `race_check.rs` tests pin the exact boundary of
    that narrow change at the unit level. Self-determinism (gate 4) confirms the change is
    fully deterministic/shuffle-invariant in self-play (where contested cells DO occur
    routinely, since both sides run the same chopper logic) — a different, weaker guarantee
    than champion-equality, not conflated with it here.

## Sizes
- `cgauto/submissions/v1.36.0-race.rs`: **72,815 B** (bundled, comments retained).
- `cgauto/submissions/v1.36.0-race.min.rs`: **43,306 B** (57% under the 100,000 B cap).
- `data/candidates/v1.36.0-race/v1.36.0-race.rs` / `.min.rs`: byte-identical (`cmp`-verified)
  to the `cgauto/submissions/` copies above.
- `data/candidates/v1.36.0-race/v1.36.0-race.debug-probe.min.rs`: **43,305 B** (DEBUG=true,
  GE_MAX_TROLLS=2 confirmed present by grep).

## Diffstat
```
rust/src/botmain.rs         |  4 +-  (VERSION, GE_MAX_TROLLS + comment)
rust/src/botmain/planner.rs | 60 ++++++++++++++++++++++++++++++++++++++------ (race check)
rust/tests/tactics_scale.rs |  8 ++++  (4x #[ignore] + comment)
rust/tests/race_check.rs    | new file, 2 tests
```

## Next steps (gatekeeper)
`collect_debug_games.py <probe> boss 8` + field (incl. denial-style mikdiet 6480914 / plcc
6480966, and >=1 >=19.6 player per `field_targets.py`). This candidate is a pure waste-cut
(never chases a losing race, joins winnable ones at a small discount) with NO training/farm/
funding changes, so the expected signature is: wood/economy numbers in the existing Tempo-era
band (should NOT move much — this isn't an economy lever, it's an execution/efficiency fix),
possibly a small reduction in wasted-travel turns on maps with contested/shared trees, and
zero effect on games where the two players' chop zones never overlap. `ramp.py --last 8` for
wood/delta as usual; no crater expected given the narrow, discount-only nature of the change
(never larger than avoiding one bad multi-turn trek).

## Arena verdict (2026-07-07 22:24) — KEEP, new CHAMPION

Boss/field gate was WAIVED for this candidate under the arena-queue idle-slot policy
(2026-07-07): pure waste-cut, no pie risk, diagnostic probe games left optional for later. Ran
directly through the arena-runner procedure (full detail + table also logged in
`docs/silver-experiment-log.md` under "v1.36.0-race arena verdict").

**Bracket (pre-submit):** 21:34:12 MSK — ARENA-ROOM rank 117/527, Gold score **18.6** (agentId
6542490). **Submit:** 21:34:21, SUBMIT-OK (TestSession 40964539).

**Convergence reads (agentId 6542530 confirmed live throughout):**
| time | Δt | rank | score |
|---|---|---|---|
| 21:54:29 | +20m | 116/527 | 18.6 |
| 22:09:17 | +35m | 88/527 | 20.1 |
| 22:24:24 | +50m | 103/527 | 19.9 |

Shape: flat-at-bracket -> climb -> flatten (20.1 -> 19.9, Δ0.2). Steady-climb-to-flat, clears
KEEP bar (bracket−0.2 = 18.4) by ~1.3-1.5 pts. Decided at +50, not ambiguous.

**Decision: KEEP.** Since the converged score is clearly above the bracket (not parity),
`cgauto/api_submit.py`'s default path was updated to `submissions/v1.36.0-race.min.rs` (it had
gone stale pointing at `v1.28.2-steady2.min.rs`, already behind the true prior champion
v1.28.3-sticky6). v1.36.0-race is now the standing arena champion; `docs/arena-queue.md`
Champion/Queue/Verdict-log sections updated to match.

This is the largest single-candidate arena jump of the whole T-hand/protection cycle, and the
first clean positive result since sticky6 — notable because the change is execution-only (no
economy/training move), suggesting wasted travel into doomed shared-tree races was costing more
field points than the recent economy-side experiments were able to recover.

**Handoff to analyst:** run `battles.py 40`, confirm the shift traces to fewer wasted-trek
losses (pull 1-2 loss replays, compare command mixes) rather than variance, and decide whether
v1.37.0-nanaflow's champion-equality gate should now target v1.36.0-race instead of sticky6.
