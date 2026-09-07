# PROGRESS — chopup (all times real UTC, `date -u`)

- 01:24 read CLAUDE.md / AGENTS.md / WORKFLOW.md / WORKSTATE.md / EVALUATION.md,
  then the parked `hirewood` run 20260907T005717Z-3869329-1 (RESULT, PLAN, TSV).
  Confirmed its loss was broad stat re-pricing: 168/192 hires changed, mostly
  `ms` 2->1. That model is parked and is NOT extended here; no fruit term added.
- 01:25-01:29 read the parent's real opening code in
  `claude_candidate_policy_flat.rs` (`ensure_opening`, `opening_objective`,
  `collection_eta`, `opening_key`, `choose_second_troll`, `training_affordable`,
  `strongest_affordable`, `enforce_training_deadline`) and the referee prices.
- 01:29-01:31 wrote `claude_candidate_chopup.py` (five guarded unique-anchor
  replacements) and `test_claude_candidate_chopup.rs`.
- 01:30 PLAN.md frozen: ONE eligibility/payback rule and the gate, written
  before any test or panel row existed.
- 01:31 generate: compact export 91,043 UTF-16 (limit 100,000) using the same
  already-proven guarded `DEAD_REGIONS` pruning, with keep-guards on the live
  first-hire code. Parent sha 95ee691e verified by the generator, fail-closed.
- 01:31 rustc 1.90.0 `--test` build clean, 0 errors, 11.5 s.
- 01:32 first run: 18 passed, 1 FAILED. `a_barren_forest_keeps_the_parent_spec`
  was wrong in the fixture, not the rule: `board(1, 0, ..)` still carries seven
  size-4 orchard trees, so there IS felling work and buying chop is correct.
  Replaced it with the real finite-horizon rejection (`a_spent_horizon_...`) and
  recorded the bare-stand case as a printed observation, not a rejection claim.
- 01:32 second run: 20 passed, 0 failed, 1 ignored (trace). `tests.log`.
- 01:32-01:33 bench FIRST, nothing else running: 16 serial streams on the pruned
  source, absolute rustc 1.90.0. 4,312 turns, mean 1.77 ms, p95 10.6 ms, max
  26.1 ms (readable) / 27.0 ms (compact), over_50ms 0, and exact
  readable-vs-compact command equality `packaging_different_games` 0.
- 01:33-01:34 ONE panel binary built, run-local `CARGO_TARGET_DIR`, 83 s,
  binary 37d736c3.
- 01:34-01:39 ONE panel: 192 pairs, 9947500..9947507, both seats, 12 opponents,
  `ALLOW_ANY_MAP_SEED=1`, 273.157 s, exit 0.
- 01:39 result: candidate stream identical to baseline in **192/192** pairs.
  Delta +0.0. All 192 baseline command streams match gap 210944Z exactly; the
  only differing baseline column is the `baseline_divergent_command` diagnostic,
  empty here precisely because the arms never diverge.
- 01:40 process table clean: no rustc/cargo/panel/test/bench process left,
  nothing detached. Hashes recorded. GATE FAILS (needs positive) -> PARK.
