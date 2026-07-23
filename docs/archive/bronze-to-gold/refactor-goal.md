# GOAL: Three-layer bot refactor with provably zero behavior change

> **✅ COMPLETED 2026-07-06 ~16:45** — all four criteria executed:
> (1) **500-game equality EQUAL (0 divergences)** on the final layered structure vs the frozen
> reference; (2) 18 suites / 28 tests green; (3) minified single file **92,071 B < 100 KB**
> compiles (`submissions/v1.25.0-layers.min.rs`); (4) arena hold-check run: v1.25.0-layers
> converged 128 @ 17.3 vs contemporaneous baseline 17.8 (day's same-code drift 17.8-18.6) —
> outside the strict ±0.2, inside observed drift; **conservative branch taken: v1.20.0
> resubmitted 16:45 → the baseline ends intact** (as this goal prescribes). Final structure:
> `src/botmain/{state,motion,tactics,jobs}.rs`, decide_elite = plan → assign_all → watchdog
> (15 lines). Open follow-up (R5.0): seeded-rh_rand tiebreaks instead of lexicographic if the
> −0.5 recurs. Details: docs/silver-experiment-log.md 2026-07-06 15:40-16:45 entries.

Refactor the Troll Farm bot into the three-layer architecture — **L1 tactics / L2 job
assignment / L3 motion** — with provably zero behavior change. Extract `decide_elite` and its
state types from `rust/src/main.rs` into library modules (`main.rs` becomes a thin stdin
shim), guarded by an **equality harness**: the refactored bot must emit **identical command
streams to the frozen v1.20.0 baseline** (`cgauto/submissions/v1.20.0-motion.rs`) over
**≥500 simulated games** (fixed seeds, both seats).

## Done when ALL of these hold

1. **Harness green on the final layered structure**: command streams identical to the frozen
   v1.20.0 baseline over ≥500 sim games (fixed seeds, both seats).
2. **`cargo test --release` green**, including `motion_corridor`.
3. **Minified submission compiles**: `tools/minify.py` output builds with
   `rustc --edition 2021` and is < 100 KB.
4. **Arena hold-check**: the refactored bot, submitted via `cgauto/api_submit.py`, converges
   (two ARENA-ROOM reads ≥15 min apart, movement < 0.1) **within ±0.2 of the 118 @ 18.6
   baseline** — then either it stays live or v1.20.0 is resubmitted; either way the baseline
   ends intact.

## Explicitly OUT of scope

**No policy or behavior changes of any kind in this goal** — no new knobs, no tuning, no
"while I'm here" fixes. Behavior-changing L2 experiments (farm-supply invariant, starter role
by marginal value, feeder-as-a-job) are the follow-up goal that this one unlocks.

## Amendments (2026-07-06, R1 execution — discovered constraints, criteria unchanged in spirit)

1. **Reference = v1.20.0 + two determinizing tiebreaks** (frozen:
   `cgauto/submissions/v1.25.0-ref-deterministic.rs`, binary `rust/target/refactor/reference_bin`).
   Literal stream-equality vs raw v1.20.0 is IMPOSSIBLE — it is nondeterministic (HashSet
   iteration ties break randomly per process; proven: it diverges from itself). The two
   tiebreak lines (`free_base`, funding-iron pick: `(score, cell)` keys) are by construction
   value-neutral (they only order equal-scored options) and are the ONLY stream-unproven
   deltas; the arena hold-check (criterion 4) covers exactly them. Everything after is
   stream-proven against this reference.
2. **`const VERSION` is frozen at "1.25.0-layers" for the whole refactor** — the turn-1
   `MSG v{VERSION}` is part of the equality-checked stream.
3. **Equality opponent = a bot binary (the frozen reference) or scripted WAIT**, never a lib
   roster strategy (those carry their own per-process nondeterminism). Harness:
   `rust/src/bin/equality.rs` — usage `equality <botA> <botB> <seeds> [max_turns] [opp]`.
4. **Module extraction may require a bundler**: CG accepts ONE source file. If `decide_elite`
   moves to library modules, the submission is produced by concatenating them back into a
   single file (tool + rustc compile-gate), or, as fallback, the layers become in-file
   `mod {}` blocks inside main.rs. Criterion 3 (minified single file compiles < 100 KB)
   stays the gate either way.

## Context (for the executing agent)

- Plan and milestones: `docs/ROADMAP.md` Phase R (R1 harness → R2 extract motion → R3 extract
  jobs → R4 tactics). Working tree is already restored to the exact v1.20.0 source.
- The harness compares against the **frozen artifact**, not "the code before the last edit" —
  the reference must not drift during the work.
- The arena check exists because sim-equality does not cover the minify/submit path.
- Iron rules and tooling recipes: `docs/ROADMAP.md` §2-§3 (cwd discipline, `uv run --no-sync
  python`, verify by ARENA-ROOM line only, revert rule).
