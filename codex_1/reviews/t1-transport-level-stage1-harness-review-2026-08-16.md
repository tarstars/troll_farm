# T-1 stage-1 fixture harness review — 2026-08-16

Verdict: **REVISION_REQUIRED before stage 2 or any prediction grading.**

Reviewed artifact `07c983d35ba8743c56f6b8a3044ea66c83ee74d5`. Independent runs reproduce
the reported evidence:

- `fixture_harness.py --self-test`: 7/7 pass;
- resident baseline: 0 FIXED / 34;
- D1 is active for OSC-001..030; P4 is knowingly unwired for OSC-031..034.

The disclosed P4 gap is real and stage 1b remains mandatory. Two additional grader
defects block using the harness for a candidate:

## F1 — leaving the frozen two-cell set is incorrectly treated as restored progress

`grade()` defines `restored = had_progress(...) or left_the_cycle(...)`. The frozen
registry instead requires that the stuck unit reach its target or produce progress
events. Merely visiting a third cell proves neither. A candidate that converts a
two-cell oscillation into a three-cell/no-progress loop, drift, or another intention
failure can therefore become `FIXED` if D1 is quiet.

The claimed positive control depends on this relaxation: it moves the window later in
the same trace while retaining the old cycle cells, so `left_the_cycle` makes it pass.
It does not demonstrate that a genuine task-progress event can pass the grader.

Required repair: remove `left_the_cycle` as an independent success condition. Grade
against instrumented candidate intent/target or a narrowly specified progress event, as
the upstream contract requires. Add positive and negative controls including a
detector-quiet three-cell/no-progress trace.

## F2 — “exact frozen episode” fidelity is not exact

`check_replay_fidelity()` matches only `unit`, `turn_start`, and `turn_end`; it does not
compare `cells` or `k`. The self-test checks cells only for OSC-006 after the loose match,
and no all-30 assertion covers those fields. A detector can change its cycle or period
while retaining the same bounds and satisfy the supposedly exact guard.

Required repair: compare every frozen detector-defining field (`unit`, bounds, cells,
and `k`, with explicit canonicalization where ordering is non-semantic) for all 30 D1
fixtures. Make a cells-only mismatch and a k-only mismatch each fail a negative control.

## Stage-1 completion boundary

Wire the actual P4 liveness rule for OSC-031..034 and observe it firing on the resident.
Until then, the honest result is “D1 baseline partially validated; P4 and non-vacuous
progress grading incomplete,” not a completed instrument. The reconstruction map/seed
guards and the repaired overlap-key check are useful and should be retained.
