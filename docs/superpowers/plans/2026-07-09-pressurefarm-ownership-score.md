# Pressure-Farm Ownership Score Candidate Plan

> **For agentic workers:** This plan starts from the completed diagnostic in
> `docs/superpowers/plans/2026-07-09-total-map-value-ownership.md`. Use the ownership score for
> narrow behavior changes only, measure influence, and do not pursue AUROC/model-validation work in
> this plan.

**Goal:** build and measure `v1.53.0-pressurefarm`: a narrow behavior candidate that uses live
ownership pressure to reduce value donations on our half of the map.

**Architecture:** Rust behavior candidate using the existing `rust/src/botmain/ownership.rs`
diagnostic as the scoring source. The score may influence `Plan` fields and planner priorities,
but it must not become a global planner rewrite.

**Tech Stack:** Rust under `rust/src/botmain*`; DEBUG telemetry with `@TFOWN`; existing
bundle/minify/equality gates; fresh DEBUG probes via `cgauto/collect_debug_games.py`.

## Global Constraints

- Work from `/home/tarstars/prj/troll_farm`.
- Do not modify arena submission defaults until all local gates and DEBUG probes pass.
- Keep AUROC/win-loss classifier validation postponed.
- Keep behavior changes local to farm pressure: planting cap, seed-reserve release, and exposed
  local-tree liquidation.
- No static turn-only behavior. The trigger must depend on live ownership pressure.
- No global planner rewrite, broad roam widening, or opponent-side factory raid unless a later plan
  explicitly proves it.

---

### Task 0: Freeze Baseline And Score Contract

**Files:**
- Read: `rust/src/botmain/ownership.rs`
- Read: `rust/src/botmain/tactics.rs`
- Read: `rust/src/botmain/planner.rs`
- Read: `data/analysis/map-value-ownership/report.md`

**Interfaces:**
- Defines the pressure score fields that behavior may consume.
- Does not change behavior yet.

- [ ] **Step 1: Name the baseline.** Record the current bundled/minified baseline used for
  comparison.
- [ ] **Step 2: Define the behavior score.** Start with a transparent score such as:

```text
pressure = own_half_exposed + created_exposed
```

  and optionally normalize by total remaining value for reporting only.
- [ ] **Step 3: Define pressure states.**
  - Green: no material exposed local value.
  - Yellow: own-half exposed value is visible; pause expansion only if created/local value exists.
  - Orange: exposed created/local value exists; prioritize conversion.
  - Red: opponent ETA makes preserving nearby farm value worse than conversion.
- [ ] **Step 4: Keep constants visible.** Put thresholds near the ownership/farm constants and
  emit them in DEBUG telemetry.

---

### Task 1: Expose Ownership Pressure To Planning

**Files:**
- Modify: `rust/src/botmain/ownership.rs`
- Modify: `rust/src/botmain/tactics.rs`
- Modify only if needed: `rust/src/botmain.rs`

**Interfaces:**
- `ownership.rs` returns a compact pressure result from live `State`/`Plan`.
- `Plan` gains pressure fields used by planner decisions.

- [ ] **Step 1: Add a pressure struct.** Include at least `own_half_exposed`,
  `created_exposed`, `pressure_score`, and a pressure state enum/int.
- [ ] **Step 2: Compute pressure once per turn.** Avoid repeated full recomputation in planner
  hot loops.
- [ ] **Step 3: Add fields to `Plan`.** Keep field names explicit and diagnostic-friendly.
- [ ] **Step 4: Emit DEBUG telemetry.** Add either `@TFPRESS` or extend `@TFFARM` with pressure
  fields.

---

### Task 2: Add Narrow Pressure Behaviors

**Files:**
- Modify: `rust/src/botmain/planner.rs`
- Modify: `rust/src/botmain/tactics.rs`
- Modify only if constants are needed: `rust/src/botmain.rs`

**Interfaces:**
- Behavior changes only under observed pressure.

- [ ] **Step 1: Dynamic farm cap.** Under Yellow+ pressure, suppress new farm planting unless the
  farm is below a small survival floor.
- [ ] **Step 2: Seed-reserve release.** Under Orange/Red pressure, allow protected seed trees to be
  converted when the model says they are not safely ours.
- [ ] **Step 3: Exposed local-tree liquidation.** Under Orange/Red pressure, raise local farm-tree
  fell candidates before opponent arrival.
- [ ] **Step 4: Guard against over-liquidation.** Preserve normal behavior when pressure is Green,
  and reject locally if our final wood/output craters.

---

### Task 3: Measurement Gate

**Files:**
- Create: `data/candidates/v1.53.0-pressurefarm/report.md`
- Optional: `data/candidates/v1.53.0-pressurefarm/*.csv`

**Interfaces:**
- Compares candidate vs baseline on behavior output and ownership metrics.

- [ ] **Step 1: Run standard local gates.**
  - focused tests;
  - `cargo test --release`;
  - bundle compile;
  - minified compile and size check;
  - self/bundled/minified equality where expected.
- [ ] **Step 2: Run DEBUG probes.**
  - boss context;
  - at least 2 games each vs `6480966`, `6480914`, and `6480824`;
  - collect `@TFOWN` and pressure telemetry.
- [ ] **Step 3: Compare influence.** Report baseline vs candidate for:
  - final score and wood;
  - t150/t225 `own_half_exposed`;
  - t150/t225 `created_exposed`;
  - t150/t225 `opp` and `uncertain`;
  - farm count and seed reserve behavior.
- [ ] **Step 4: Decide local outcome.**
  - PASS: exposed own-half/created value falls without wood/output collapse.
  - ITERATE: pressure trigger engages but thresholds are too harsh/weak.
  - STOP: no ownership-bucket improvement or production collapses.

---

### Task 4: Arena Gate Only If Local PASS

**Files:**
- Update: `docs/arena-queue.md` only if local PASS.
- Update: `data/candidates/v1.53.0-pressurefarm/report.md`.

**Interfaces:**
- Produces an arena-ready candidate only after local evidence.

- [ ] **Step 1: Freeze candidate artifacts.**
- [ ] **Step 2: Add arena queue entry only if local PASS.**
- [ ] **Step 3: Follow arena policy v2 exactly.**

## Exit

This plan is complete when `data/candidates/v1.53.0-pressurefarm/report.md` states one of:

- `PASS: queue v1.53.0-pressurefarm`;
- `ITERATE: adjust pressure thresholds`;
- `STOP: ownership-score behavior did not improve measured outcomes`.

AUROC remains postponed until after a larger, more balanced post-candidate corpus exists.
