# PROGRESS — 20260907T024202Z-4185751-1 (orchard / near-bank fruit economy)

Real stages, `date -u` throughout. Deadline 03:27:02Z.

- 02:42-02:46 read AGENTS/WORKFLOW/WORKSTATE/EVALUATION and the ticket; read the
  parent's `SearchBot`/`YamoBot::commands`/`main_candidates`, `can_train`,
  `training_affordable`, and the referee's `apply_plant`/`apply_harvest`/
  `apply_pick`/`tick_plants`/`training_cost`/`score`. Established the parent's
  actual defect: both its PLANT paths are timber regeneration (near-bank
  `PICK BANANA` gated on `plants.len() <= 2`, plus the AppleOrchardBot mother
  tree), and `can_train`/`training_affordable` hard-stop at `n >= 2`.
- 02:47 PLAN.md frozen — mechanism, comparison, budget, pass/park gate — before
  any test or panel row existed.
- 02:47-02:52 wrote `claude_candidate_orchard.py` (five guarded unique-anchor
  replacements) and `test_claude_candidate_orchard.rs`. Readable source compiled
  clean under rustc 1.90.0 on the first attempt; compact export 92,661 UTF-16
  with the already-proven guarded `DEAD_REGIONS` pruning plus keep-guards on all
  seven live orchard functions.
- 02:50 first test run: 11 passed, 2 failed. Both failures were my fixture
  asserting things about the *parent* that are false: the parent's inherited
  AppleOrchardBot layer plants a near-bank mother tree on this board too, and
  its endgame branch issues its own PICKs. Fixed the assertions, not the rule:
  test 1 now measures the paired fruit/points and asserts the real distinction
  (workers 3 vs 2); test 5 now asserts paired dormancy against the baseline arm.
- 02:51 13 tests pass, 0 failed (10 embedded + 5 new; `tests.log`).
- 02:52 bench PASS on the pruned source, nothing else running: 16 streams,
  4,312 turns, mean 1.93 ms, p95 11.0 ms, max 27.1 ms, over_50ms 0,
  `packaging_different_games` 0.
- 02:53 panel binary built with run-local `CARGO_TARGET_DIR`, sha f0bb5cf3.
- 02:54-02:59 one panel, 192 pairs in 302.0 s, exit 0. Baseline 167/6/19
  pts=170.0 own=231.35 margin=114.43 issues=1; candidate 154/2/36 pts=155.0
  own=210.88 margin=78.88 issues=1. **Gate fails on both clauses (-15.0).**
- 02:59 control check: all 192 baseline rows, including `baseline_commands`,
  identical to run 20260906T210944Z-3184968-1; only the run-relative divergence
  columns differ (`control-check.txt`).
- 03:00 activation measured: 152/192 pairs changed commands, harvests +1,325,
  drops +1,223, chops -181, wood 35.19 vs 42.45, but **0 pairs reached three
  workers**. Checkpoints: 328/376 hold 0 IRON, and the harvest branch is not
  deficit-kind-gated (20-25 banked PLUM, 0 LEMON).
- 03:03 process table clean: no rustc/cargo/panel/test process left, nothing
  detached. RESULT.md written; PARK.
