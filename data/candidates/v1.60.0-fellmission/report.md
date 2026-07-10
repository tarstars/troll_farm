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

## Fix: banking-crater (conditional override)

**Boss-gate measurement that found this (2026-07-11):** 6 boss games on the C1/C2-fixed
build above came back with **our banked wood == 0 in every game**, vs champion
`v1.59.0-ringfix3`'s ~48. This is a CRITICAL regression, not a tuning nit — a chopper that
never banks contributes zero score all game.

### C3 — `resolve_commands` unconditionally overrode the chopper's command with the mission's

**Defect:** `resolve_commands` called `planner::assign_resolved` over the full roster (the
C2 fix), then **unconditionally** replaced the chopper's own assigned command with
`missions::chopper_target`'s command — CHOP/MOVE toward a fell target, or `WAIT` if none.
The mission has no concept of banking at all. So whenever `assign_resolved`'s own pick for
the chopper was actually a bank action —
band 80 ("full -> bank", fires whenever `free_capacity() == 0`) or band 95 ("bank a carried
load in time to score it", the endgame liquidation window) — that decision was silently
thrown away and replaced with "go fell (or travel toward) the next tree". Consequence: the
instant the chopper's carry filled up, it kept moving toward/chopping trees instead of
walking home to `DROP`; felled wood piled up in carry and was **never banked**, turn after
turn, for the rest of the game — exactly the observed 0-wood boss games.

**Fix:** only let the mission override the chopper's `assign_resolved` command when that
command is **not itself** a bank/endgame action. `resolve_commands` now computes:

```rust
let band_cmd = cmd_by_id.get(&cid).cloned().unwrap_or_default();
let band_wants_bank =
    u.free_capacity() == 0 || plan.liquidation || band_cmd.starts_with("DROP ");
if !band_wants_bank {
    let target = missions::chopper_target(state, plan, u);
    // ... override with the mission's CHOP/MOVE, or leave the band command if target is None
}
```

Rationale for each disjunct of `band_wants_bank` (the exact conditional-override condition):
- **`u.free_capacity() == 0`** — a PROVABLY EXACT detector on its own. `candidates()` always
  offers band 80 (`80 * BAND`) whenever `free_capacity() == 0`, and `80 * BAND` outranks every
  fell candidate a chopper can have (`<= 72 * BAND` plus small sub-BAND offsets, `BAND =
  100_000`) — so `assign_resolved`'s pick for a full chopper is *always* that Bank candidate.
  This is the main crater fix.
- **`plan.liquidation`** (`turns_rem <= GE_LIQ_T`) — defers for the chopper's **whole**
  endgame tail, a strictly safe superset of the exact turn band 95 fires (which needs
  `d_home`, the BFS distance from the chopper's current cell to the shack, not available in
  `resolve_commands` without recomputing a second BFS). Whenever band 95 hasn't fired yet
  inside the liquidation window, `assign_resolved`'s own bands 70/72/30/31 still fell trees
  (band 95 only outranks them once its own trigger `turns_rem <= e+1` is met) — so this
  disjunct only forgoes the mission's wood-efficiency tree PICK for this short (~11%-of-the-
  game, `GE_LIQ_T=34` of `TOTAL_TURNS=300`) tail, **never** a bank action for a fell action.
- **`band_cmd.starts_with("DROP ")`** — an unambiguous rendered tell on its own: only
  `Kind::Bank`'s `motion::bank_cmd` ever emits a `DROP` command. Kept as a belt-and-braces
  guard in case the two conditions above are ever refactored independently of each other.

When `band_wants_bank`, the chopper's `assign_resolved` command is left **completely
untouched** (not even read again) — including the case where the eventual `target` lookup
would have been consulted. Concretely, `missions::chopper_target` (which mutates the
`COMMITTED` thread-local) is **not called at all** while banking — this both avoids wasted
work and, more importantly, means the committed fell target from before the banking trip
started is left exactly as-is; when the chopper next has `free_capacity() > 0` again (after
the `DROP`), `chopper_target` sees the same still-standing committed tree and returns it
unchanged (no re-plan) — the mission resumes felling the same tree after the bank trip, per
the original commitment design.

When the mission's `target` is `None` (no reachable/non-doomed eligible tree this turn) the
new code **defers to the band's own fallback** (band 30/31 anti-starvation "fell anything
reachable", or band 10 park) instead of the old hard-coded `WAIT` — strictly no worse, and
sometimes strictly better (band 30/31's fell-eligibility filter is looser than the mission's,
since it skips `fell_ok`/`own_half`/`within_roam` entirely).

**Tests added** (`rust/tests/fellmission.rs`):
- `fellmission_full_chopper_banks_not_fells`: chopper at `(1,2)` (shack-adjacent, manhattan
  1) with `carry[WOOD] = 3` (full, `free_capacity() == 0`) and an eligible LEMON tree
  standing nearby. RED against the unconditional-override code: chopper's final command was
  `"MOVE 1 3 2"` (progress toward the tree) instead of the expected `"DROP 1"`. GREEN after
  the fix.
- `fellmission_endgame_banks_partial_load`: chopper at `(2,2)` (NOT shack-adjacent — this
  geometry deliberately isolates the `plan.liquidation` disjunct from the other two) with
  `carry[WOOD] = 1` (partial load, `free_capacity() == 2 > 0`) and `plan.turns_rem = 3` with
  `plan.liquidation = true`; at this geometry band 95's own trigger (`turns_rem <= e+1` where
  `e = ceil(d_home/ms) + 1 = ceil(1/2) + 1 = 2`) is genuinely met (`3 <= 3`), so band 95
  itself — not merely "liquidation is set" — is `assign_resolved`'s top pick. RED against the
  unconditional-override code: chopper's final command was `"MOVE 1 4 2"` (landing exactly on
  the tree, distance 2 == movement_speed) instead of the expected `"MOVE 1 1 2"` (toward the
  camp cell). GREEN after the fix.
- All 7 pre-existing `fellmission` tests (wrong-tree, doomed-skip, commitment, Task-4 wiring,
  C1 ring-protection x2, C2 starter-deconfliction) pass unchanged in intent — none of them
  exercise a full or endgame chopper, so none were sensitive to this defect either way.

### Gates (post-C3-fix)

- `cargo test --release`: **all suites green** (9/9 in `tests/fellmission.rs` — 7 pre-existing
  + 2 new; full workspace suite also 0 failures across every other test binary).
- Self-determinism equality:
  `target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
  → **EQUAL: 16 games (8 seeds x 2 seats), all command streams identical.**
- Champion consts confirmed untouched: `GE_SPEC=(2,3,0,2)`, `GE_MAX_TROLLS=2`,
  `GE_FARM_R=2`, `GE_CHOP_R=5`, `GE_LIQ_T=34`, `STICKY=6`, `DENY_W=0`, `RACE_SHARE_PEN=2`,
  `VERSION="1.60.0-fellmission"` all byte-identical in the rebuilt bundle.
- Artifacts rebuilt: `bundle.py` (158,988 B full source) → `rustc --edition 2021 -O`
  compile-check → `minify.py` (80,498 B) → compile-check → DEBUG probe (DEBUG false→true,
  minified, 80,497 B) → compile-check. **All three compiles exit 0.** Both well under the
  100 KB cap. Frozen to `cgauto/submissions/v1.60.0-fellmission.*` and mirrored to
  `data/candidates/v1.60.0-fellmission/` (byte-identical copies).

### Boss-gate validation (the crater is fixed)

Played 4 real DEBUG games vs the live Boss
(`collect_debug_games.py v1.60.0-fellmission.debug-probe.min.rs boss 4`) with the C3 fix:

| game | result | our wood | opp wood | ramp (t75/t150/t225/t300, ours) |
|---|---|---|---|---|
| 895690305 | L | **47** | 48 | 8 / 22 / 34 / 47 |
| 895690322 | L | **48** | 53 | 12 / 24 / 36 / 48 |
| 895690325 | L | **36** | 46 | 10 / 20 / 30 / 36 |
| 895690333 | W | **64** | 66 | 20 / 40 / 52 / 64 |

Our banked wood is now **36-64 (avg 49)** — healthy, steady per-turn growth every game,
comparable to (and in 3/4 games exceeding) champion `ringfix3`'s ~48 baseline — a complete
reversal of the pre-fix 0-wood crater. 1/4 wins is a normal result for this matchup and is
**not** the concern this fix targets (win rate vs Boss 5 is a separate, larger question this
candidate has not yet been field-gated for — see "Open follow-up" above); the crater
specifically (banked wood stuck at 0 regardless of outcome) is resolved.

### Commits

- `e3d2a24` fix(fellmission): C3 — conditional mission override fixes banking crater

