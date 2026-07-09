# v1.53.0-pressurefarm — builder report

Scope: Tasks 0-2 of `docs/superpowers/plans/2026-07-09-pressurefarm-ownership-score.md`
(score contract -> expose pressure to `Plan` -> three narrow pressure behaviors). Tasks 3
(measurement gate) and 4 (arena) are NOT done here -- this report leaves the candidate
gate-ready for the next pipeline stage.

Base: champion line `73d1d39` (VERSION `1.46.0-splitclaims` = v1.43.0-yield + v1.46.0
fruit/wood tree-claims + the `ownership.rs` telemetry module). The worktree slot was found
at a stale Bronze-era commit (`fa33b21`) at the start of this session -- verified
`session-2026-07-01` was a clean ancestor and fast-forwarded before starting any work.

## What changed, and where

### Task 0 -- score contract (folded into Task 1's types; no standalone behavior)

`rust/src/botmain/ownership.rs` gains, alongside the UNCHANGED `analyze`/`classify_tree`/
`Ownership` diagnostic:

```rust
pub enum PressureState { Green, Yellow, Orange, Red }  // derived Ord: Green < Yellow < Orange < Red

pub struct Pressure {
    pub own_half_exposed: i32,
    pub created_exposed: i32,
    pub pressure_score: i32,              // = own_half_exposed + created_exposed
    pub state: PressureState,
    pub exposed_created_cells: HashSet<Cell>,   // created/farm trees classified Opponent|Uncertain
    pub released_seed_cells: HashSet<Cell>,     // seed_cells released from protection (see below)
}
```

Ladder (`classify_pressure`, private fn):
- **Green**: `own_half_exposed == 0` (no exposed value anywhere on our half; implies
  `created_exposed == 0` too since created trees are a subset of own-half trees in practice).
- **Yellow**: `own_half_exposed > 0`, `created_exposed == 0` -- some value on our half is
  contestable, but nothing WE planted is at stake yet.
- **Orange**: `created_exposed > 0` -- a created/local farm tree is itself Opponent- or
  Uncertain-bucketed (per the existing `classify_tree` ETA race).
- **Red**: Orange's condition **plus** at least one created-exposed tree is *definitively*
  opponent-bound (`Bucket::Opponent`, not merely `Bucket::Uncertain` -- i.e. the opponent's
  ETA beats ours even after the existing 3-turn margin). This is the literal encoding of
  "opponent ETA makes preserving nearby farm value worse than conversion."

`ownership::assess(state, plan) -> Pressure` computes this once by calling the UNCHANGED
`analyze()` plus one extra pass bounded by created-farm-tree count (not map size).

### Task 1 -- expose pressure to planning

`rust/src/botmain/tactics.rs`: `Plan` gains exactly **one** new field,
`pub pressure: ownership::Pressure`, computed once per turn in `plan_impl` via a two-phase
build (a `provisional` Plan with farm_d/farm_r/seed_cells already final -> `ownership::assess`
-> the one derived override, `farm_cap` -> final `Plan { farm_cap, pressure, ..provisional }`).
Never recomputed in `planner.rs`'s per-troll hot loop. (Single field, not six loose ones --
this bounded the mechanical ripple to the ~14 existing test files that build `Plan` by hand
to ONE new line each, `pressure: ownership::Pressure::default()`.)

`rust/src/botmain.rs`: VERSION bump; new constant
`GE_PRESSURE_FARM_FLOOR: usize = 4` (near the other `GE_FARM_*` constants); DEBUG call site
extended: `ownership::log(state, &plan); ownership::log_pressure(state, &plan);`.

DEBUG telemetry (Task 1 Step 4): `@TFPRESSCFG farm_floor=4` once at turn 1;
`@TFPRESS t=<t> own_half_exposed=<> created_exposed=<> pressure_score=<> state=<Green|
Yellow|Orange|Red> exposed_n=<> released_n=<>` at the same cadence as `@TFOWN` (t=75/150/
225/300 and every 5 turns) -- reads `plan.pressure` directly, no recomputation.

### Task 2 -- three narrow pressure behaviors

All three are gated so Green is a **provable no-op** (see below), never a static/turn-only
trigger, and never "always smaller/always earlier" -- the diagnostic's binding constraint.

1. **Dynamic farm cap** (`tactics.rs`, Step 1): under `state >= Yellow`,
   `farm_cap = provisional.farm_cap.min(GE_PRESSURE_FARM_FLOOR)`. A farm already below the
   floor is unaffected -- the clamp only ever lowers a ceiling the farm hasn't reached, never
   forces liquidation. This is the ONLY behavior gated on Yellow; the other two need Orange/
   Red (created value must actually be at stake before liquidating/releasing anything).
2. **Seed-reserve release** (`planner.rs` `fell_ok`, Step 2): a seed-protected tree
   (`plan.seed_cells`) stays protected unless it is in `plan.pressure.released_seed_cells`.
   That set is deliberately **stricter** than `exposed_created_cells`: it only contains a
   seed cell whose own tree is bucket `Opponent` (not merely `Uncertain`), gated additionally
   on the aggregate `state >= Orange`. Seed supply is the most dangerous lever in this
   codebase's history (deforestation stalls when it dies), so release requires the harder,
   per-tree signal, not just "the aggregate state escalated somewhere."
3. **Exposed local-tree liquidation priority** (`planner.rs` `candidates()`, Step 3): under
   `state >= Orange`, a tree in `exposed_created_cells` gets `+PRESSURE_LIQ_BONUS` (= 4, a
   new `planner.rs`-local constant beside `STICKY`/`DENY_W`/`RACE_SHARE_PEN`) added to its
   band-70/72 (chopper primary fell) and band-40/42 (starter chop-help) candidate value --
   less than one BAND (100,000), so it only ever re-ranks within a band, never crosses the
   priority hierarchy. Non-exposed trees are untouched (the bonus is keyed to
   `exposed_created_cells` membership, not a blanket rank change).
4. **Guard against over-liquidation** (Step 4): enforced structurally -- every behavior above
   is additionally gated by set membership (`exposed_created_cells`/`released_seed_cells`),
   never a blanket "if pressure >= X, do Y to everything." Craters/output collapse are a
   measurement-gate concern (Task 3, not mine) -- see "Gate needs" below.

## TDD: RED evidence (each mechanism temporarily neutralized, test rerun, then restored)

| Test | Neutralization | Captured failure |
|---|---|---|
| `pressure_green_is_noop` | dropped the `!` negation in `fell_ok`'s seed check (a realistic slip) | `Green must keep the seed tree protected: CHOP 2` (expected `MOVE 2 5 2`) |
| `tactics_farm_cap_floor_engages_under_yellow_but_not_below_floor` | `farm_cap` override forced to `if false { .. }` | `Yellow with base_trees above the floor must clamp farm_cap to the floor, got 12` (expected 4) |
| `orange_raises_local_liquidation` | `PRESSURE_LIQ_BONUS` set to 0 | `Orange must raise the exposed, farther tree above the naturally-closer one: MOVE 2 3 2` (expected to contain "4 2") |
| `red_releases_seed_reserve` | `fell_ok`'s seed check reverted to the pre-pressure form (no release path) | `Red must release the seed tree so the chopper fells it in place: MOVE 2 5 2` (expected `CHOP 2`) |
| `assess_red_when_created_tree_definitely_opponent` | `classify_pressure`'s `definite_opponent` branch removed (always Orange) | `a definite opponent win must escalate to Red: ... state: Orange` (expected Red) -- note `released_seed_cells` stayed CORRECT even with this bug, since it recomputes its own per-tree bucket check independently of the aggregate label |

Each was reverted immediately after capturing the failure; `cargo test --release` was
confirmed green again after every revert (final full-suite run below).

Every behavior test also has a flip-check (fires in its own state, does NOT fire in the
adjacent lower state) -- see `rust/tests/pressurefarm.rs` inline.

## Gate commands + output (in order run)

```
$ cd rust && cargo test --release
... 75 passed; 0 failed; 0 ignored (across all suites) -- up from the 66-test pre-candidate
baseline (+9 new: 5 in Section A / ownership::assess wiring, 4 required behavior tests in
Section B, all in tests/pressurefarm.rs)

$ ./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ uv run --no-sync python tools/bundle.py
src/botmain.rs -> target/refactor/bundled.rs: 116754 chars

$ rustc --edition 2021 -O <bundled copy>          # exit 0, compiles
$ ./target/release/equality <bundled> target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ uv run --no-sync python tools/minify.py target/refactor/v1.53.0-pressurefarm.rs \
    target/refactor/v1.53.0-pressurefarm.min.rs
116754 -> 71390 chars (61%)

$ rustc --edition 2021 -O <minified copy>         # exit 0, compiles
$ ./target/release/equality <minified> target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' \
    target/refactor/v1.53.0-pressurefarm.rs > .../v1.53.0-pressurefarm.debug.rs
$ uv run --no-sync python tools/minify.py <debug.rs> <debug-probe.min.rs>
116753 -> 71389 chars (61%)
$ rustc --edition 2021 -O <debug-probe.min.rs copy>   # exit 0, compiles
```

DEBUG-probe smoke test (hand-fed static input, see below): stdout starts with
`MSG v1.53.0-pressurefarm;CHOP 0`; stderr contains all expected tags --
`@TFMAP @TFI @TFD @TFSUM @TFMOVE @TFFARM @TFOWNCFG @TFOWN @TFPRESSCFG @TFPRESS`.

## Green-noop evidence (three independent layers)

1. **Structural**: all three behaviors are gated by conditions that are provably false
   whenever `pressure.state == Green` -- `farm_cap`'s `if pressure.state >= Yellow` branch,
   `fell_ok`'s `released_seed_cells` (populated only when `state >= Orange`), and
   `pressure_bonus`'s `state >= Orange` check. Under Green these aren't just empirically
   inert, they're unreachable by construction.
2. **Unit test** `pressure_green_is_noop` (3 sub-checks: plant-vs-bank, liquidation bonus,
   seed protection) -- PASS, with RED evidence above proving each sub-check actually
   discriminates.
3. **Constructed binary-level equality** (base vs candidate, real compiled binaries): built
   the pre-candidate base binary via `git stash` (champion `73d1d39`, VERSION
   `1.46.0-splitclaims`), then hand-crafted a static repeated-snapshot CG-protocol input (10x5
   map, opponent troll far away at the opposite corner with chop_power=1, our chopper
   standing on a banana at size 2) fed for 20 turns. `diff` of the two binaries' stdout over
   this input: **IDENTICAL**. A DEBUG-enabled build of the SAME candidate on the SAME input
   confirms `state=Green` at every checkpoint (t=5,10,15,20) throughout -- closing the loop
   between "the scenario really is Green" and "the two binaries really produce the same
   output there."

**Note for the gatekeeper**: I also tried a *naturally-occurring* Green window across random
seeds (the existing `equality` harness's Bronze-map generator, `max_turns` capped small).
This did **not** stay clean -- e.g. seed=2 diverges by turn 5. I traced this one case with a
scratch instrumented driver (not committed) and confirmed it is genuine: `own_half_exposed`
reaches 19 by turn 5 on that map (a native/wild tree contested on our geometric half), so
`state` is already `Yellow` and the farm-cap clamp is correctly, intentionally firing -- not a
bug. This matches the diagnostic report's own finding that `own_half_exposed` is often
substantial by the *earliest* measured checkpoint (t=75, field avg 52.0) and shows it can
develop even earlier purely from map geometry. So a clean natural Green window across random
seeds is **not reliably constructible** (the plan's own "(if constructible)" wording
anticipated this); the hand-constructed scenario above is the rigorous substitute.

## Pressure struct + thresholds (for the gatekeeper's telemetry read)

| Constant | Value | File | Meaning |
|---|---:|---|---|
| `GE_PRESSURE_FARM_FLOOR` | 4 | `botmain.rs` | Yellow+ clamps `farm_cap` down to this (never below current `base_trees`) |
| `PRESSURE_LIQ_BONUS` | 4 | `planner.rs` | Orange+ within-band bump for an `exposed_created_cells` fell candidate |
| seed release gate | `state >= Orange` **and** that tree's bucket `== Opponent` | `ownership.rs` (`assess`) | deliberately stricter than the broader `exposed_created_cells` test |

`@TFPRESS` fields map 1:1 onto `Pressure`'s fields; `@TFOWN`'s `created_exposed`/
`own_half_exposed` (unchanged existing diagnostic) should numerically match `@TFPRESS`'s
same-named fields at the same turn (same underlying `analyze()` call; confirms no drift
between the old diagnostic and the new governor).

## Artifact sizes

| File | Bytes |
|---|---:|
| `v1.53.0-pressurefarm.rs` (bundled) | 118,256 |
| `v1.53.0-pressurefarm.min.rs` | 71,390 |
| `v1.53.0-pressurefarm.debug-probe.min.rs` (DEBUG=true) | 71,389 |

All well under the 100,000-byte submission cap.

## Gate needs (for the gatekeeper)

Standard local gates are done (table above). For Task 3 (measurement gate), compare
candidate vs baseline (current champion, `v1.46.0-splitclaims`-equivalent) on:

- final score and wood (t300).
- t150 and t225 `own_half_exposed` (from `@TFPRESS`, cross-checked against `@TFOWN`'s same
  field) -- PASS signal = candidate's value is lower than baseline's without a wood/score
  collapse.
- t150 and t225 `created_exposed` (same cross-check).
- t150/t225 `@TFOWN`'s `opp`/`uncertain` buckets, to see whether suppressing our own
  expansion actually reduces the map value we hand the opponent, or just shrinks the total
  pie without changing the split.
- farm count (`@TFFARM`'s `farm=`) and seed-reserve behavior (`released_n` in `@TFPRESS`,
  should be 0 almost always and only nonzero under genuine Red pressure) -- a `released_n`
  that's frequently nonzero on ordinary games would indicate the seed-release gate is firing
  too eagerly and needs tightening before an arena attempt.
- `PASS` requires exposed own-half/created value to fall without wood/output craters (per the
  plan's Task 3 Step 4 decision rule); `ITERATE` if the trigger engages but
  `GE_PRESSURE_FARM_FLOOR`/`PRESSURE_LIQ_BONUS` look too harsh/weak from the numbers; `STOP`
  if there's no ownership-bucket improvement or production collapses.

Suggested probe set (per the plan's Task 3 Step 2): boss context + >=2 games each vs
`6480966`/`6480914`/`6480824` (matching the diagnostic corpus in
`data/analysis/map-value-ownership/report.md`), collecting `@TFOWN` + `@TFPRESS`.

## Concerns / things the gatekeeper should know

- The candidate's own DEBUG-instrumented run (turn ~5, one Bronze-map seed) already shows
  Yellow firing early and often -- the farm-cap clamp is NOT a rare-event mechanism, it will
  be live in most games by mid-game. That is by design (this is the point of the feature),
  but it means the wood/output-collapse check in Task 3 matters more than it might for a
  narrower trigger.
- `PRESSURE_LIQ_BONUS=4` and `GE_PRESSURE_FARM_FLOOR=4` are untuned first values (chosen to
  be "small, in the same order of magnitude as `STICKY`/`RACE_SHARE_PEN`" per the plan's
  "keep constants visible" instruction) -- Task 3's numbers are the first real signal on
  whether they're too weak/harsh.
- I did not implement the design doc's optional "late raid response" (opponent-factory
  targeting) -- out of scope per the plan's Task 2 (three behaviors only) and the Global
  Constraints ("no ... opponent-side factory raid unless a later plan explicitly proves it").
- Determinism: all new `HashSet<Cell>` fields (`exposed_created_cells`, `released_seed_cells`)
  are only ever `.contains()`-queried by consuming code, never iterated for ordered output --
  confirmed no new sort-order dependency was introduced (see the doc comment on
  `ownership::assess`).

## Fix: C2 Orange-gate + I1 race-safe liq bonus (review follow-up)

Two targeted fixes from the code review (NEEDS_FIXES: one CRITICAL, one IMPORTANT), applied
surgically in-place -- no architectural changes.

### C2 (CRITICAL) -- farm-cap clamp re-gated Yellow -> Orange

**Bug**: `tactics.rs`'s dynamic farm-cap clamp fired on `pressure.state >= Yellow`. Yellow only
requires `own_half_exposed > 0` (`created_exposed == 0`) -- a signal that lights up from static
map geometry (any own-half tree we can't *prove* decisively ours), near-permanent from ~turn 5
on real maps, independent of any real threat to farm value we created. Gating the clamp there
collapsed `farm_cap` 12->4 for essentially the whole game: the "always smaller farm" nerf this
feature's own design explicitly forbids, and a throughput crater (dense-farm-never-idle is this
bot's whole economic thesis).

**Fix**: re-gated to `pressure.state >= ownership::PressureState::Orange` (`rust/src/botmain/
tactics.rs`, the `farm_cap` `if`/`else` right after `ownership::assess`). Orange requires
`created_exposed > 0` -- a created/local farm tree the ownership model itself marks
not-safely-ours -- which is threat-discriminating (needs the opponent's ETA to actually contest
a tree *we planted*), matching the plan's Task 0 Step 3 ("Yellow: ... pause expansion ONLY IF
created/local value exists") and `data/analysis/map-value-ownership/report.md`'s recommended
trigger. Green/Yellow both now leave `provisional.farm_cap` untouched; only Orange/Red clamp to
`GE_PRESSURE_FARM_FLOOR` (4), still floored so a farm already below it keeps its normal room to
grow.

**M1 (MINOR, latent note only)**: added a one-line comment at the clamp site flagging that
`Phase::Factory`'s `farm_cap = 20` would be overridden by this clamp if Orange+ pressure ever
fires during Factory. Dormant today (`GE_META = Tempo`, Factory unreachable) -- no logic added.

**Test update** (`rust/tests/pressurefarm.rs`): the old
`tactics_farm_cap_floor_engages_under_yellow_but_not_below_floor` (which asserted Yellow itself
clamped to the floor -- the bug, encoded as the expected behavior) is replaced by
`tactics_farm_cap_clamps_on_orange_not_yellow`. New helpers `orange_initial`/`orange_scenario`
build a genuinely Orange (not Red) fixture: a created BANANA farm tree at (2,2) is engineered to
a near-tie (`|6-5|=1 < OWN_MARGIN_TURNS(3)`) against an opposing chopper standing on it ->
`Bucket::Uncertain` -> `created_exposed > 0` -> Orange, never escalating to Red; the other four
farm-radius candidates are all safely ours (the opponent's return trip to its own distant shack
is far too long to contest them), so exactly one tree drives `created_exposed`. The rewritten
test asserts, as a single flip-check: Yellow (`yellow_scenario(5)`) leaves `farm_cap` at the
champion value (12, NOT clamped); the Orange fixture (`orange_scenario(5)`) clamps to the floor
(4); and a below-floor Orange fixture (`orange_scenario(3)`) still leaves plantable room
(`base_trees < farm_cap`).

**RED evidence** (captured against the pre-fix, still-Yellow-gated code, before touching
`tactics.rs`):
```
thread 'tactics_farm_cap_clamps_on_orange_not_yellow' panicked at tests/pressurefarm.rs:762:5:
assertion `left == right` failed: Yellow ALONE (own_half_exposed>0, created_exposed==0) must NOT clamp farm_cap -- that was the C2 bug (an 'always smaller farm' nerf firing from mere map geometry), got 4
  left: 4
 right: 12
```
GREEN after the re-gate (see gate output below); the Orange-clamps-to-4 and below-floor
sub-assertions in the same test were never reached pre-fix (the function panics at the first
failing `assert_eq!`) but both pass cleanly post-fix, confirming the `orange_scenario` ETA
arithmetic lands exactly Orange (not Red) on the first try.

### I1 (IMPORTANT) -- PRESSURE_LIQ_BONUS made race-safe

**Bug**: `PRESSURE_LIQ_BONUS` (4) > `RACE_SHARE_PEN` (2). `planner.rs`'s `pressure_bonus`
closure added the bonus unconditionally to any `exposed_created_cells` fell candidate,
including one that is *also* a joinable contested race (`race()` returned `Some(RACE_SHARE_PEN)`
-- an enemy is already chopping it, but we can still arrive in time to share the wood). Net
effect on such a tree: `-RACE_SHARE_PEN(2) + PRESSURE_LIQ_BONUS(4) = +2` -- the race check's
tuned "don't over-trek to a shared/discounted tree" discount was not just canceled but
*reversed into a preference*, locally undoing part of the v1.36.0-race behavior credited with
the champion's +1.3 arena gain.

**Fix**: `pressure_bonus` now takes `race_pen` as a second parameter (`rust/src/botmain/
planner.rs`) and returns `0` whenever `race_pen != 0`. Both call sites (`candidates()`'s band
70/72 primary fell loop and the starter's band 40/42 chop-help loop) already compute `race_pen`
via `match race(pc, steps) { None => continue, Some(pen) => pen }` *before* the bonus is
computed, so a doomed tree (`race() == None`) never reaches `pressure_bonus` at all (it
`continue`s past the whole candidate, unchanged from before), and the only two live values of
`race_pen` at the call site are `0` (no opponent occupant -- genuinely non-contested) and
`RACE_SHARE_PEN` (a joinable race). Withholding the bonus whenever `race_pen != 0` therefore:
(a) fully preserves the bonus on every non-contested exposed tree (this behavior's primary job),
and (b) makes a contested tree's net adjustment exactly `-race_pen` either way -- i.e. it can
never exceed its un-pressured, race-discounted value, closing the reversal with margin to
spare (not just capping it at parity).

**Test added** (`rust/tests/pressurefarm.rs`): `orange_liq_bonus_is_race_safe`, mirroring
`orange_raises_local_liquidation`'s exact geometry (chopper at (1,2); trees at (3,2)/(4,2), both
size 2, so (4,2) is naturally 1 in-band step behind (3,2)) but adding a winnable enemy chopper
standing on (4,2) (health 4, chop_power 1 -> `their_turns=4 > our_eta=2`, joinable not doomed)
while marking (4,2) exposed/Orange. Asserts the chopper still targets (3,2), not (4,2) (the
contested exposed tree is not lifted above its race-discounted value); a flip-check then removes
the enemy occupant (same Orange/exposed marking, now genuinely non-contested) and asserts (4,2)
now wins via the full, untouched liquidation bonus -- reproducing `orange_raises_local_
liquidation`'s outcome in the same test so the discriminator (contested vs not) is visible in
one place.

**RED evidence** (captured against the pre-fix, unconditional-bonus code, before touching
`planner.rs`):
```
thread 'orange_liq_bonus_is_race_safe' panicked at tests/pressurefarm.rs:522:5:
a joinable-contested exposed tree must NOT be lifted above its un-pressured (race-discounted) value: MOVE 2 4 2
```
(the chopper moved to the contested (4,2) instead of the discount-free (3,2) -- the bonus had
flipped the race discount into a net preference, exactly the bug). GREEN after gating
`pressure_bonus` on `race_pen`.

### Gate outputs (in order run, this follow-up pass)

```
$ cd rust && cargo test --release --test pressurefarm --test race_check --test planner_tasks --test phase_factory
test result: ok. 1 passed (phase_factory: factory_plants_and_fells)
test result: ok. 3 passed (planner_tasks: contested_tree_goes_to_the_better_troll_without_duplication, priorities_hold, shuffle_invariance)
test result: ok. 10 passed (pressurefarm -- up from 9: +1 net, tactics_farm_cap_floor_engages_under_yellow_but_not_below_floor
  renamed to tactics_farm_cap_clamps_on_orange_not_yellow (+0), orange_liq_bonus_is_race_safe added (+1))
test result: ok. 2 passed; 1 ignored (race_check: doomed_contested_tree_is_skipped, winnable_contest_is_joined;
  share_pen_shifts_near_tie_to_free_tree stays #[ignore]d, untouched by either fix)

$ cargo test --release
test result: ok. 76 passed; 0 failed; ... (up from the pre-fix 75; the +1 is orange_liq_bonus_is_race_safe,
  since the C2 test was a rename not an addition) -- across all suites, no regressions

$ ./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ uv run --no-sync python tools/bundle.py src/botmain.rs target/refactor/v1.53.0-pressurefarm.rs
src/botmain.rs -> target/refactor/v1.53.0-pressurefarm.rs: 119449 chars

$ rustc --edition 2021 -O target/refactor/pressurefarm_check.rs -o target/refactor/pressurefarm_check_bin   # exit 0
$ ./target/release/equality target/refactor/pressurefarm_check_bin target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ uv run --no-sync python tools/minify.py target/refactor/v1.53.0-pressurefarm.rs target/refactor/v1.53.0-pressurefarm.min.rs
119449 -> 71484 chars (59%)

$ rustc --edition 2021 -O target/refactor/pressurefarm_min_check.rs -o target/refactor/pressurefarm_min_check_bin   # exit 0
$ ./target/release/equality target/refactor/pressurefarm_min_check_bin target/release/bot 8 300 target/release/bot
EQUAL: 16 games (8 seeds x 2 seats), all command streams identical

$ sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' target/refactor/v1.53.0-pressurefarm.rs \
    > target/refactor/v1.53.0-pressurefarm.debug.rs
$ uv run --no-sync python tools/minify.py target/refactor/v1.53.0-pressurefarm.debug.rs target/refactor/v1.53.0-pressurefarm.debug-probe.min.rs
119448 -> 71483 chars (59%)
$ rustc --edition 2021 -O target/refactor/pressurefarm_debug_check.rs -o target/refactor/pressurefarm_debug_check_bin   # exit 0
```

### Updated artifact sizes (bytes, `wc -c`; the char counts above are from Python's `len()`
and differ slightly because the source uses multi-byte em-dashes in comments)

| File | Bytes |
|---|---:|
| `v1.53.0-pressurefarm.rs` (bundled) | 120,969 |
| `v1.53.0-pressurefarm.min.rs` | 71,484 |
| `v1.53.0-pressurefarm.debug-probe.min.rs` (DEBUG=true) | 71,483 |

All well under the 100,000-byte submission cap. `cgauto/submissions/v1.53.0-pressurefarm.{rs,
min.rs}` and `data/candidates/v1.53.0-pressurefarm/v1.53.0-pressurefarm.{rs,min.rs,
debug-probe.min.rs}` were all regenerated from this pass and are byte-identical to each other
pairwise (submissions vs candidates copies).
