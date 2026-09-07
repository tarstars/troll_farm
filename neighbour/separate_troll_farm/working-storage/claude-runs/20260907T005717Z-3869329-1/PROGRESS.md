# PROGRESS — 20260907T005717Z-3869329-1 (hirewood / first-hire wood investment)

Real stages, `date -u` throughout. Deadline 01:47:17Z.

- 00:57–01:02 read AGENTS/WORKFLOW/WORKSTATE/EVALUATION and the ticket; read the
  parent's `opening_objective` / `opening_key` / `choose_second_troll` /
  `strongest_affordable` / `enforce_training_deadline` and the referee's
  `training_cost`, `apply_chop`, `predict_tree`, `chop_outcome`, `score`.
  Established the parent's actual defect: `opening_key`'s leading component is
  the raw stat sum, so a point of speed, carry and chop are interchangeable.
- 01:02–01:06 wrote `claude_candidate_hirewood.py` (five guarded unique-anchor
  replacements) and `test_claude_candidate_hirewood.rs`; the test export also
  carries the untouched parent as `mod baseline`, so both arms play one referee.
- 01:07 `rustc 1.90.0 --test` build clean on the first attempt (0 errors).
- 01:07 PLAN.md frozen — mechanism, comparison, budget and the pass/park gate —
  before any test or panel row existed.
- 01:08 first run: 11 passed, 4 failed, all "candidate must hire". Trace fixture
  (`debug_opening_trace`) showed the cause was my board, not the rule: with an
  empty bank a 4-turn carry-1 round trip per fruit cannot fund any hire before
  `hard_train_turn`. `official_mapgen` deals each player 2..=10 of every
  resource but wood; board corrected to a realistic part-funded state.
- 01:10 second run: 13 passed. Decision really changes (candidate 1/3/0/1 vs
  parent 2/2/0/1), bill and spawn exact. Barren board failed: the hire was
  valued at the forest the *starter* would have felled anyway.
- 01:11 fixed that in the rule, not the fixture: `hire_value` now claims the
  standing forest for the trolls already on the board first and prices the hire
  at the margin (`hire_trips` / `claim_trips`). Barren board then buys the fast
  cheap hire, as predicted in PLAN.
- 01:11 unpruned compact export was 100,334 UTF-16 units, over the limit. Reused
  the already-proven `DEAD_REGIONS` guarded pruning for the compact export only,
  with explicit keep-guards on the live first-hire code: 90,365 units.
- 01:12 rich-board superiority assertion **failed and was not forced**: the
  candidate buys carry 3, the parent buys speed 2, and on that board the parent
  banks more (24 wood / 105 points vs 22 / 98). The fixture now measures and
  prints the pair instead of asserting a win it does not have.
- 01:13 15 tests pass (7 new + 8 embedded, both modules), 0 failed, 1 ignored
  trace fixture. `tests.log`.
- 01:14 serial 16-stream bench launched on the *pruned* source (the one that is
  minified into the shipped compact), absolute rustc 1.90.0, nothing else
  running.
- 01:14 bench PASS on the pruned source: 4,312 turns, mean 1.78 ms, p95 10.6 ms,
  max 27.3 ms, over_50ms 0, `packaging_different_games` 0, rustc 1.90.0.
- 01:14–01:20 one panel, run-local `CARGO_TARGET_DIR`, binary f30e5429:
  192 pairs in 286.161 s, exit 0. Baseline 167/6/19 pts=170.0 (identical to the
  gap 210944Z control arm), candidate 163/1/28 pts=163.5, issues 1 vs 0.
  **Gate 1 fails (-6.5).** 168/192 pairs changed the first hire, 72 changed its
  turn; the change is almost always `ms` 2→1. No opponent gained.
- 01:20 process table clean: no rustc/cargo/panel/test process left. Nothing
  detached. RESULT.md written; PARK.
