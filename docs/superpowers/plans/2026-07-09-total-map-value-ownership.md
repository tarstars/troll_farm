# Total Map Value Ownership Diagnostic Plan

> **For agentic workers:** Use the Superpowers plan style: execute task-by-task, update
> checkboxes as work completes, and do not build an arena behavior candidate until the
> diagnostic produces evidence. This plan implements the diagnostic-only next step from
> `docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`.

**Goal:** determine whether losses contain a repeatable ownership leak: value that existed or
was created earlier, was not safely ours, and later became opponent score/wood.

**Architecture:** Rust read-only diagnostic inside the DEBUG bot over the live per-turn
`State`. The bot emits ownership rows such as `@TFOWN`; optional Python tooling only aggregates
those rows into the report. No planner behavior changes, no arena submit, no candidate freeze in
this plan.

**Tech Stack:** Rust under `rust/src/botmain*` for the diagnostic model and DEBUG emission,
local DEBUG/raw artifacts under `data/boss5_games/`, existing collection via
`cgauto/collect_debug_games.py`, and optional Python under `uv run --no-sync python` for
aggregation/report generation.

## Global Constraints

- Work from `/home/tarstars/prj/troll_farm`.
- Do not modify arena submission defaults.
- Rust changes are allowed only for side-effect-free diagnostic computation and DEBUG logging.
- Do not change planner choices, training gates, action ranking, arena queue entries, or candidate
  defaults in this plan.
- Existing raw/debug games are useful context, but exact ownership verdicts require new DEBUG games
  after `@TFOWN` exists because older raw files do not contain per-turn tree snapshots.
- The first scoring model can be rough; it must be transparent and easy to audit.
- Output must answer whether `v1.53.0-pressurefarm` is justified, not implement it.

---

### Task 0: Confirm telemetry and sample set

**Files:**
- Read: `data/boss5_games/**/game_*.raw`
- Read: `rust/src/botmain.rs`
- Read: `rust/src/botmain/state.rs`
- Read: `rust/src/botmain/tactics.rs`
- Read: `cgauto/battle_taxonomy.py`
- Read: `cgauto/motion_analyze.py`
- Read: `cgauto/collect_debug_games.py`

**Interfaces:**
- Documents what current raw artifacts can and cannot prove.
- Produces a short note in the final diagnostic report describing which newly collected
  `@TFOWN` games were analyzed, plus which old games were used only as context.

- [x] **Step 1: Inventory available raw games.** Count `.raw` files by opponent directory under
  `data/boss5_games/`. Prioritize `6480966` (`plcc`), `6480914` (`mikdiet`), `6480824`
  (`kurigen`), and `boss` if present.
- [x] **Step 2: Verify old raw inputs.** Confirm existing raw files contain:
  - `@TFMAP` rows;
  - initial `@TFI P` tree rows;
  - per-turn `@TFD` rows with inventories and unit positions;
  - `@TFSUM` rows with score, inventory, tree count, and builds.
- [x] **Step 3: Confirm the blocker in old raw.** Record that older raw files do not contain
  per-turn tree coordinates, so they cannot produce exact total-map ownership buckets at
  t75/t150/t225.
- [x] **Step 4: Confirm Rust has the real state.** Verify `State` contains live `trees`,
  `my_trolls`, `opp_trolls`, inventories, shacks, and walkable cells before each decision.
- [x] **Step 5: Pick the exact diagnostic corpus.** After Rust emits `@TFOWN`, collect at least
  2 DEBUG games each from `plcc`, `mikdiet`, and `kurigen` when available. Add boss/local games
  only as extra context, not as the primary verdict.

---

### Task 1: Build the Rust read-only ownership diagnostic

**Files:**
- Create: `rust/src/botmain/ownership.rs`
- Modify: `rust/src/botmain.rs`
- Modify only if needed for module wiring: nearby `rust/src/botmain*.rs`

**Interfaces:**
- Consumes live Rust `State` and, if useful, the current `Plan`.
- Emits `@TFOWN` rows to stderr in DEBUG builds.
- Does not feed ownership results back into planner behavior.

- [x] **Step 1: Add diagnostic data structures and constants.**
  - Define visible constants for bucket margin, farm radius, created-value source rules, and
    future-value addends.
  - Define a compact result struct with `total`, `ours`, `opp`, `uncertain`, `dead`,
    `created_exposed`, and `own_half_exposed`.
  - Keep all diagnostic state internal to the module and side-effect-free except DEBUG logging.
- [x] **Step 2: Track initial tree cells for created-value detection.**
  - On turn 1, snapshot initial tree positions/types inside the diagnostic module.
  - Treat later banana trees in our farm radius or near our tent that were not in the snapshot as
    created farm value.
  - Reset this diagnostic snapshot on new games.
- [x] **Step 3: Implement BFS helpers over live map state.**
  - Reuse simple grid BFS over `state.walkable`.
  - Compute distance from each current worker to each tree cell.
  - Compute distance from each worker to own/opp tent-adjacent bank cells.
- [x] **Step 4: Implement worker capability extraction from live trolls.**
  - Suitable wood worker: `chop_power > 0`; strong chopper: `chop_power >= 2`.
  - Suitable fruit worker: `harvest_power > 0`.
  - Use `movement_speed`, `carry_capacity`, current carry, and remaining turns in ETA/payoff
    estimates.
- [x] **Step 5: Wire DEBUG emission.**
  - Emit a `@TFOWNCFG` line at turn 1 with the constants used.
  - Emit `@TFOWN` at t75, t150, t225, and t300; emitting every 5 turns is acceptable if cheaper
    for report narratives.
  - Include `early=1` or equivalent if a game ends before t300 and a final row is emitted.

---

### Task 2: Score value ownership buckets

**Files:**
- Modify: `rust/src/botmain/ownership.rs`

**Interfaces:**
- Produces one ownership row per game/phase:

```text
@TFOWN t=150 total=180 ours=72 opp=55 uncertain=41 dead=12 created_exposed=18 own_half_exposed=25
```

- [x] **Step 1: Score live tree value coarsely.**
  - Wood value: `4 * size`.
  - Ripe fruit value: `fruits`.
  - Optional future/seed value: small fixed addend for ripe banana/apple seed sources; keep this
    simple and document the constant.
- [x] **Step 2: Classify likely owner.**
  - `ours`: our best suitable ETA + action time beats opponent by a margin.
  - `opponent`: opponent best suitable ETA + action time beats us by a margin.
  - `uncertain`: ETAs are close or both sides can plausibly contest.
  - `dead`: no suitable worker can reach/capture/bank it before the game ends.
- [x] **Step 3: Track created/exposed value.**
  - Count created farm value as banana trees within our farm radius or near our tent that were not
    present in the turn-1 diagnostic snapshot.
  - Count created value as exposed when bucket is `opponent` or `uncertain`.
- [x] **Step 4: Track own-half exposed value.**
  - Use distance to my tent vs opponent tent to classify halves.
  - Count non-owned value on our half separately; this is the likely feedstock for late raids.
- [x] **Step 5: Keep constants visible.**
  - Put bucket margins, farm radius, and future-value addends near the top of the Rust module.
  - Print them in `@TFOWNCFG` and the aggregate report so later agents can judge sensitivity.

---

### Task 3: Run the diagnostic and write the report

**Files:**
- Create: `data/analysis/map-value-ownership/report.md`
- Optional: `data/analysis/map-value-ownership/*.csv`
- Optional: `cgauto/map_value_ownership.py`

**Interfaces:**
- Consumes `@TFOWN` rows from newly collected DEBUG raw artifacts.
- Produces a written verdict: proceed to pressure-farm candidate, collect more data, or stop.

- [x] **Step 1: Build a DEBUG bot with `@TFOWN`.** Use the repo's existing bundle/minify flow
  for a DEBUG build; do not change arena submission defaults.
- [x] **Step 2: Collect prioritized field probes.**

```bash
uv run --no-sync python cgauto/collect_debug_games.py <debug-with-tfown.min.rs> 6480966 2
uv run --no-sync python cgauto/collect_debug_games.py <debug-with-tfown.min.rs> 6480914 2
uv run --no-sync python cgauto/collect_debug_games.py <debug-with-tfown.min.rs> 6480824 2
```

- [x] **Step 3: Collect boss/local context if useful.**

```bash
uv run --no-sync python cgauto/collect_debug_games.py <debug-with-tfown.min.rs> boss 4
```

- [x] **Step 4: Aggregate `@TFOWN` rows.**
  - A small Python helper is allowed here if `rg`/spreadsheet-style manual aggregation becomes
    tedious.
  - It should parse `@TFOWN`/`@TFOWNCFG`, join final win/loss scores from `.log` or `@TFSUM`, and
    emit CSV/table data only.
- [x] **Step 5: Write the report.** Include:
  - corpus summary;
  - bucket averages by phase;
  - win/loss split where final score is available;
  - top 5 games by `created_exposed` at t150/t225;
  - top 5 games by `own_half_exposed` at t150/t225;
  - at least one concrete replay narrative if a leak is visible.
- [x] **Step 6: Update the spec or short notes only if the diagnostic changes the theory.**
  Do not edit arena queue yet unless a concrete candidate is queued.

---

### Task 4: Decision gate

**Files:**
- Update: `data/analysis/map-value-ownership/report.md`
- Optional update: `docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`

**Interfaces:**
- Produces the next action.

- [x] **Step 1: Decide one of three outcomes.**
  - **PROCEED:** losses show high exposed created/own-half value before the late opponent burst.
    Next plan should build `v1.53.0-pressurefarm`.
  - **MORE DATA:** signal is plausible but too thin; collect targeted DEBUG games against the
    missing opponent type.
  - **STOP:** no repeatable ownership leak; keep total-map ownership as a strategic model but
    do not spend an arena candidate on it.
- [x] **Step 2: If PROCEED, draft the candidate brief.** The brief should specify exactly which
  narrow behavior changes are allowed:
  - dynamic farm cap under observed pressure;
  - seed-reserve release under observed pressure;
  - exposed farm tree liquidation;
  - no global planner rewrite.
- [x] **Step 3: If MORE DATA, name exact opponent IDs and game count.** Not applicable:
  report chose `PROCEED`.
- [x] **Step 4: If STOP, add the rejected reason to the report.** Not applicable:
  report chose `PROCEED`.

## Exit

This plan is complete when `data/analysis/map-value-ownership/report.md` states one of:

- `PROCEED: build v1.53.0-pressurefarm`;
- `MORE DATA: collect <opponents/games>`;
- `STOP: no repeatable ownership leak`.

Only the `PROCEED` outcome should create a behavior implementation plan.
