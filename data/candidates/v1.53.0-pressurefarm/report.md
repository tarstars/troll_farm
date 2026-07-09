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
