# v1.60.0-fellmission — report

Base: v1.59.0-ringfix3 (champion). The chopper (chop_power >= 2) runs one explicit, committed
FellForWood mission (`rust/src/botmain/missions.rs`) instead of the weighted fell bands
(planner.rs bands 70/72 primary-fell, 42/40 chop-help, 31/30 anti-starvation); every other
troll's behavior is intended to stay byte-identical to ringfix3. See
`docs/superpowers/plans/2026-07-10-fellmission.md` for the original implementation plan
(Tasks 1-6) and `docs/superpowers/specs/2026-07-10-intent-missions-design.md` for the design.

## Fix: C1 ring-protection + C2 starter-deconfliction

Code review (2026-07-11) found two CRITICAL defects in the Task 2-4 implementation that would
crater the proven +1.7 economy if shipped as-is. Both are fixed on top of the original
implementation commits (`0b639fd`..`261709d`); this section documents the fixes.

### C1 — `fell_target` ignored the champion's fell-band eligibility filters

**Defect:** `missions::fell_target` iterated every `state.trees`, filtered only by
reachable + `chops > 0` + `planner::race` (the doomed-tree check). It did **not** apply the
three other fell-eligibility filters the champion's fell bands (`planner.rs candidates()`
bands 70/72/40/42) apply: `fell_ok` (protects the ring diagonal seed/fruit engine, `seed_cells`,
and honors `liquidation`/`raid`), `own_half`, and `within_roam`. Consequence: our own standing
diagonal seed-banana (small/soft, Chebyshev-1 from the shack) scores far higher on raw
wood-efficiency (`size*1000/(steps+chops)`) than any native tree, so the committed mission could
target and fell our own ring economy — the exact mechanism the champion's bands were built to
avoid (v1.56.0-ringfarm).

**Fix:**
- Extracted `fell_ok`, `own_half`, `within_roam` out of `candidates()`'s local closures into
  module-level `pub(crate) fn`s in `rust/src/botmain/planner.rs` taking `plan: &Plan` and
  `p: &Tree` explicitly — the same convention as the earlier `race` extraction (v1.60.0-fellmission
  Task 1). `fell_ok` recomputes the tiny (<=8-cell) diagonal-ring set from `plan.ring` on each
  call instead of hoisting it once per `candidates()` invocation (negligible cost, verbatim
  logic, no behavior change).
- `candidates()`'s two internal call sites (bands 70/72 and 40/42) now call
  `fell_ok(plan, p) && own_half(plan, p) && within_roam(plan, p)` explicitly — behavior-preserving,
  confirmed by the untouched 95-test baseline suite and 8-seed self-determinism equality.
- `missions::fell_target` and `missions::chopper_target` now take `plan: &Plan` and skip any
  tree failing this same predicate before scoring efficiency. The mission changes **how** we
  pick among the champion's eligible trees (max efficiency + commit); it never changes **which**
  trees are eligible.
- `botmain::resolve_commands` threads `plan` through to `missions::chopper_target`.

**Tests added** (`rust/tests/fellmission.rs`):
- `fellmission_never_fells_protected_ring_diagonal`: a standing diagonal ring banana
  (size 4, health 2, eff = 4000/3 = 1333) vs a native LEMON (size 4, health 12, eff =
  4000/8 = 500), both within realistic champion-const roam of the shack. RED against the
  unfiltered code — `fell_target` returned `Some((1,1))` (the diagonal) instead of the expected
  `Some((4,2))` (the native tree). GREEN after the fix.
- `fellmission_ring_protection_lifted_under_liquidation`: same geometry, `plan.liquidation =
  true` — confirms the diagonal's protection is lifted via the same liquidation/raid escape
  hatch the champion's own bands use (not a blanket ban), and the diagonal wins on efficiency
  as raw math suggests.
- The three pre-existing `fell_target`/`chopper_target` tests (wrong-tree, doomed-skip,
  commitment) were updated to thread a `plan` through; a new `permissive_plan` test helper
  (`opp` moved far away, `chop_r` raised to 1000) isolates their hand-picked coordinates —
  chosen for clean manhattan arithmetic on a chopper far from the shack, never meant to exercise
  realistic farm-radius placement — from the new C1 filters. The Task 4 wiring test's tree was
  relocated from `(8,2)` to `(4,2)` to stay within `base_plan`'s real `chop_r(5)` roam of the
  shack `(0,2)`.

### C2 — `resolve_commands` excluded the chopper from `assign_resolved`, breaking starter deconfliction

**Defect:** `resolve_commands` computed `others` (every troll except the chopper) and called
`planner::assign_resolved(state, plan, &others)` — the chopper was never part of the roster the
joint matcher (`select_assignments`) reasons about. A chop_power=1 STARTER (the real starting
troll, `mapgen.rs` ms=1/cc=1/hp=1/chop=1) emits chop-help (band 42/40) and anti-starvation
(31/30) Wood-claim candidates; in ringfix3 these are jointly deconflicted against the chopper's
own band-70/72 Wood claim via `claims_conflict` (same-cell Wood-vs-Wood claims always conflict).
With the chopper excluded from `assign_resolved`'s roster, that deconfliction never happens —
the starter's assignment could silently diverge from what ringfix3's own joint matcher would
ever have produced, including grabbing a tree the chopper's mission needs.

**Fix:** `resolve_commands` now calls `planner::assign_resolved(state, plan, my)` over the
**full** roster (chopper included). The chopper's own assigned command from that call is
discarded and overridden with its mission command (`missions::chopper_target`), unchanged from
before. The trailing whole-roster joint move-solve
(`planner::move_intents` + `motion::solve_moves` + `planner::pin_landing`) needed no change — it
was already re-run after the override. Accepted second-order effect: `assign_resolved`'s
internal yield-pass and `LAST_TGT` (STICKY) bookkeeping run once against the chopper's
(discarded) band assignment before the override; this does not affect the starter's claim
deconfliction, which is decided by `select_assignments` before any yield-pass or STICKY update.

**Test added** (`rust/tests/fellmission.rs`):
- `fellmission_starter_deconfliction_preserved_with_real_starter_spec`: a chop_power=1 starter
  at `(2,2)` and the chopper at `(6,2)`, two candidate trees — Tree A `(4,2)`, the best pick for
  *both* (starter chop-help value ~3,999,994; chopper fell value ~6,999,997, which always
  dominates on the same cell), and Tree B `(0,4)`, each one's clearly-worse fallback. The joint
  maximum over non-conflicting assignments is (starter -> B, chopper -> A) at total 10,999,989,
  strictly above awarding A to the starter (10,999,988) — so a correct full-roster matcher must
  push the starter onto B. RED against the `&others` code: the starter's command
  (`"MOVE 0 3 2"`, heading toward Tree A) diverged from a full-roster `assign_resolved` baseline
  (`"MOVE 0 1 2"`, heading toward Tree B). GREEN after the fix (byte-identical to the baseline).
  The existing Task 4 wiring test used a chop_power=0 gatherer, which has zero overlap with any
  fell band and so cannot exercise this path — this is the chop_power=1 case the review called
  for.
  - Implementation note for future maintainers: `planner::reset()` must be called between the
    `resolve_commands` measurement and the baseline `assign_resolved` measurement in this test.
    Both functions write the STICKY (`LAST_TGT`) thread-local as a side effect
    (`render_assignments(..., update_last_target=true)`); without an intervening reset,
    whichever call runs second picks up a same-cell STICKY bonus (+6) toward whatever the first
    call already chose, which is large enough to mask the exact conflict this test exists to
    catch (discovered empirically while designing the test — an initial version without the
    reset passed even against the unfixed code).

### Gates (post-fix)

- `cargo test --release`: **98 passed, 0 failed** (95 baseline + 2 new C1 tests + 1 new C2
  test). Pre-existing wrong-tree / doomed-skip / commitment / Task-4-wiring tests all still
  pass unchanged in intent.
- Self-determinism equality (`target/release/equality target/release/bot target/release/bot 8
  300 target/release/bot`): **EQUAL — 16 games (8 seeds x 2 seats), all command streams
  identical.** Run after each fix.
- Champion consts confirmed untouched: zero `const` diff lines in `botmain.rs`/`planner.rs`
  across both fix commits (`GE_CHOP_R=5`, `GE_MAX_TROLLS=2`, `GE_FARM_R=2`, `STICKY=6`,
  `DENY_W=0`, `RACE_SHARE_PEN=2`), and `tactics.rs` (where `Plan.farm_fell` is set to
  `if econ_b { 3 } else { 2 }`, i.e. `farm_fell=2` in econ A) has zero diff at all across both
  commits — neither fix touched it.
- Artifacts rebuilt: bundle (`tools/bundle.py`) -> rustc `--edition 2021 -O` compile-check (full
  source, 155292 bytes) -> minify (`tools/minify.py`, 80188 bytes, well under the 100 KB cap) ->
  compile-check the minified copy -> DEBUG probe (DEBUG false->true, minified, 80187 bytes) ->
  compile-check. All four compiles exit 0. Frozen to `cgauto/submissions/v1.60.0-fellmission.*`
  and mirrored to `data/candidates/v1.60.0-fellmission/`.

### Commits

- `da8604a` fix(fellmission): C1 — fell_target must respect ring/seed/roam protections
- `cab37da` fix(fellmission): C2 — keep the chopper in assign_resolved for starter deconfliction

### Open follow-up (not blocking)

This candidate has not yet been re-run through the paired-vs-ringfix3 field gate (original plan
Task 6) with these two fixes applied — that gate should be re-run before any arena promotion
decision, since C1/C2 change the mission's tree selection and the starter's assignment in any
game where a diagonal ring cell would otherwise have been the efficiency-argmax, or where a
chop-capable starter and the chopper contest the same tree.
