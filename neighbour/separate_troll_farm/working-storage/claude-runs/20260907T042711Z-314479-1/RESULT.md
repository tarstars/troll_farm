# RESULT — movement repaired: 26,313 issues -> 0, deficit -92.5 -> -39.0; gate still fails

**Verdict: PARK.** Legality half of the gate PASSES (zero candidate issues);
the points half FAILS (131.0 vs 170.0). No tuning was done after the panel.

**Actual reproducer.** `reproduce_blocked_move.py` replays the recorded
`candidate_commands` of run 236341's `panel.tsv` under the referee's own
`apply_resolved_moves` rule. Map 9947500 seat 0 vs gold_adaptive turn 164,
`MOVE 0 10 7 | DROP 3 | WAIT`: unit 0 (9,7)->(10,7) while unit 5 holds (10,7)
and ends the turn stationary. 24,425 reconstructed vs the runner's 26,313.
Unit 5 was still a MOVE when unit 0 was cleared — the later-cancellation cascade.

**Cause / fix.** `emit()` de-conflicted in one pass over slot order. The referee
already walks vacating chains and circular swaps, so the real invariant is only
*distinct own end-of-turn cells, none on the shack while TRAIN is pending*.
`claude_candidate_dispatch_core.rs` now uses `goal_cell`, loaded-workers-first
landing order, `reroute` (nearest free reachable cell strictly closer to goal —
the congested-door path), then a cancel-only closure that drops the
lower-priority side; cancelling never creates a mover, so it terminates.
Job values, specs, economics, TRAIN/PICK unchanged. No BFS-minus-own-units.

**Counter fixed.** The frozen model's lean `LegalityReport` has no non-critical
field, so `run()` could only sum criticals. It now compares each MOVE endpoint
with the post-step position: `issues = critical + blocked`; same-cell MOVEs are
counted separately as harmless no-ops. Shared model untouched.

**Tests: 20 run, 20 pass** (rustc 1.90.0 absolute path, `--test-threads=1`).
New `a_saturated_bank_door_never_strands_the_worker_behind_it` rebuilds turn
164's shape: **12 blocked moves on the archived pre-fix core, 0 after, all three
loads still banked** (`tests-prefix-reproducer.log`) — a differential proof.

**Export (before the panel).** pruned 281,189 -> **compact 99,652 UTF-16**
(<=100,000) via the proven `DEAD_REGIONS`/`minify` path; both compile clean in
2.4s. **16 archived streams, 4,312 turns: readable == compact, 0 mismatches**,
worst 0.051 ms/turn (`stream-equality.json`; whole-process mean, not isolated
per-turn max).

**Panel** (9947500..07, 12 opponents, both seats, `ALLOW_ANY_MAP_SEED=1`,
just-built runner `96b929ae`). Baseline 167/6/19=170.0; candidate
**130/2/60=131.0**, delta **-39.0** (was -92.5). Issues **0 vs 26,313**. Wood
23.3->36.95 (base 42.45); 186/192 hire, 3.94 workers. All 192 baseline command
streams match the 20260906T210944Z-3184968-1 controls (0 mismatches). Worst:
resident -9.0, gold_adaptive/silver_boss -5.0.

**Limitations.** Legality is fixed; the economy still loses. Hashes in
`hashes.txt` (core `651eb076`, compact `83d158aa`). Production files unchanged.

**Next action.** Attack the -39.0 economy gap, not movement: the 4-worker
roster earns less per worker than the 2-worker baseline.
