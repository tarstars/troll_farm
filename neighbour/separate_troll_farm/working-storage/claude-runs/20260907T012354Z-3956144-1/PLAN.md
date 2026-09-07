# PLAN — chopup: one conditional +1 chop on the parent's first hire
Frozen 2026-09-07T01:47Z, before any test or panel row existed.

## Mechanism (ONE fixed eligibility/payback rule, decided prospectively)
`choose_second_troll` runs exactly as the parent wrote it and its answer is kept:
movement, carry and harvest are frozen. One single alternative is then considered,
`chop_power + 1` (hard cap 3). It is bought iff ALL of:
1. chosen chop < max_chop_power.clamp(1,3) and chosen eta < 10_000;
2. the map has iron (`!view.iron.is_empty()`); with no ore the referee charges no
   iron and the parent has already taken the strongest chop it could;
3. the upgraded `opening_objective` eta is finite (<10_000) and within the
   parent's own patience window `min(chosen_eta + max_extra_eta, hard deadline)`;
4. `chop_plan` (built ONCE at the parent's spec, so tree selection is identical in
   both quotes) is non-empty; each standing plant taken at most once, load capped
   by carry, walk bounded by the remaining horizon;
5. re-walking that same plan at each spec with `predict_tree` at real arrival time:
   upgraded wood >= parent wood, upgraded elapsed clock still fits the game, and
   `parent_felling_turns - upgraded_felling_turns > extra_eta`.
Decision cached in `ensure_opening`; parent's spec cached in `opening_fallback`
and restored by `enforce_training_deadline` if the ore never arrives.

## Comparison and gate (frozen before opening the panel)
- rustc 1.90.0 `--test` on `claude_candidate_chopup_a_tests.rs` (parent compiled
  beside it as `mod baseline`; both arms play one referee).
- Serial 16-stream `benchmark_lookahead.py --games 16` on the pruned source,
  absolute rustc 1.90.0, nothing else running: max < 50 ms and exact
  readable-vs-compact command equality (`packaging_different_games` 0). FIRST.
- ONE panel: 192 pairs, seeds 9947500..9947507, 12 opponents, both seats,
  `ALLOW_ANY_MAP_SEED=1`. All 192 baseline command streams must match the
  gap 210944Z control arm (baseline 167/6/19, pts 170.0, issues 1).
- GATE: positive whole-game W+0.5D delta AND zero candidate issues over all 192.
  Report full W/D/L, score, margin, per-opponent, and exact spec-change counts;
  movement/carry changes must be 0.
- Anything else is a PARK. A fixture that does not win is reported as a
  limitation, not relabelled proof.
