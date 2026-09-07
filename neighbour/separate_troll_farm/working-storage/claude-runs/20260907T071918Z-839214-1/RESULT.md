# RESULT — self-destruction repaired; repaired plan prices below the parent and never opens

**Verdict: PARK.** The trace confirmed a fixable self-destruction and an
ownership defect; both are repaired and unit-verified. But once the commitment
pays for preserving its own supply it prices below the parent at every real
window turn and self-rejects. **No paid plan, therefore NO 192-pair panel**
(gate honoured); no compact/latency/equality certification attempted.

**Trace (first, before edits).** 9947505 seat 1, unmodified known map, adaptive
resident, real referee. t60 activate `(2,1,1,1)` bill `[P6,L3,A3,-,I3,-]`, eta
36. `LEMON@6,4` felled by **enemy** unit 2 (h8->0, t63-66). `LEMON@13,5` felled
by **our own** unit 3 (`hp=0`, never an acquirer) under the parent's
unoverridden `CHOP 3` at t66/67/68, h8->6->3->gone. Unit 1 meanwhile shuttled
the abundant PLUM at distance 0 from our door. t76 cancel, `bank=[6,0,8,4,3,3]`:
3/4 funded, no LEMON alive. The `move_blocked` is ours: overriding unit 1 to
`HARVEST` pinned it on 12,1, the cell the parent had routed unit 3 into (t72/73).

**Repair (one candidate).** (1) sources ordered by `slack = standing supply −
deficit` before distance; (2) a tree is protected from our own unoverridden
`CHOP` only when it is this turn's claim or its kind has no slack — the worker
is redirected to another tree, not idled; (3) a parent `MOVE` ending on a
re-tasked worker's cell is shortened along its own target. Claims lapse on
payment/cancellation.

**Changed files** (owned family only): `claude_candidate_macroplan_core.rs`
e65e74c7, `test_claude_candidate_macroplan.rs` f4bd8e7c; generated `_a.rs`
542e1b75, `_a_module.rs` 3843fd31, `_a_tests.rs` 461bfb1b; unchanged
`_control_module.rs` 526cd9cc, `.py` e3cc05c8. Prior family in `archive-065010/`.

**Tests: 18 run, 18 pass**, rustc **1.90.0**, `--test-threads=1`: the 13
retained plus scarcity-before-distance, own-source survival, banked-fruit-needs-
no-tree, retasked-worker-never-blocks-parent-move, release-after-pay/cancel.

**Real map, 16 pairs (9947500..07, both seats, adaptive opponent 0), ON/OFF.**
0 activations. 16/16 bit-identical to the parent, W+0.5D 10.0 vs 10.0, issues
0 vs 0 (the observed `move_blocked` is gone). Rollout prices t40/t60 both seats:
macro − parent = −17.0, −8.06, −1.40, −6.85.

**Evidence.** `TRACE-EVIDENCE.md`, `trace.log`, `price.log`, `activation2.tsv`,
`tests-3.log`, `make_trace.py`.

**Limitations.** No acquisition/payment/spawn on a real map, so no panel and no
export/latency/equality run. Opponent index 0 only. Endpoint repair covers
parent-vs-overridden collisions only. Fixtures are constructed states. All jobs
collected; none running.

**Next action.** Owner decision: aim the repaired controller at a bill the
parent's own stock already covers (no fruit acquisition), or close the
third-troll family — at horizon 60 the seed is spent ~turn 100 and cannot repay
15 resource units before the checkpoint, and the horizon is frozen.
