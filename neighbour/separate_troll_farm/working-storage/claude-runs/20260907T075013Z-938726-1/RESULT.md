# RESULT — runnable seed→wood candidate, gate FAILED, defect named. No panel.

**Verdict: do not promote.** A complete, runnable, parent-anchored BANANA cycle
exists and activates on real maps, but the first behavioural gate fails: sum
Δscore **−51** over 16 controls and **50 candidate issues** on one row. Per the
ticket no 192-panel was run; the budget went to diagnosis.

**Changed files (all NEW, mine only).** Parent `95ee691e`, `bot.rs` `44e3daca`,
`submission.rs` `7f61a6cd` **unchanged**.
`claude_candidate_seedplan_core.rs` `d26b8e62`; `claude_candidate_seedplan.py`
`42a2a106`; `test_claude_candidate_seedplan.rs` `38f5e78e`; generated
`_a.rs` `bcee3784` (310,763 UTF-16), `_a_module.rs` `a5d102e0`,
`_a_tests.rs` `051156c0`, `_control_module.rs` `526cd9cc`.

**Tests.** `rustc -O --test claude_candidate_seedplan_a_tests.rs`;
`build/seedplan_tests --test-threads=1` → **24 pass / 0 fail** (`tests-4.log`
pre-repair, `tests-repair.log` post-repair). Covers referee growth/health laws,
capacity-tied target, cc1+hp0 full cycle, growth served by parent work, PICK/PLANT
non-displacement, plot protection by redirection, disruption/endgame/deadline
cancellation, joint legality, clone isolation, disabled-parent identity, live
active-search activation. **rustc 1.97.1 — 1.90 is not installed here**, so the
1.90 gate was not met.

**Gate** (maps 9947500..07, both seats, adaptive opponent index 1, OFF=parent vs
ON=candidate, same state): 9/16 rows diverge; OFF 3402 pts / ON 3348; wood 629→646;
W/D/L 14-0-2 both arms; **Δ −64** pre-repair, **−51** after one liveness repair.
One row dominates: 9947503 seat 1, Δ −67, `no_capacity:46, move_blocked:4`.

**Named defect (confirmed by trace).** The plan **strands its withdrawn seed in
the owned worker's pack**. `diag503b.err`: turn 47 worker 1 (cc1) holds the BANANA
one step from its plot; the parent issues `PICK 1 APPLE`; the never-displace rule
defers; deferral-cancel at turn 50 releases the worker **still full**; at turn 55+
the parent re-issues the same illegal `PICK` every turn to game end. Deferring to a
command the referee refuses, then cancelling without unloading, costs that worker's
whole game.

**Evidence** (run dir): `PLAN.md`, `gate16{,-repaired}.tsv/-summary.txt`,
`defect.txt`, `worker-correlation.txt`, `diag503.err`, `diag503b.err`,
`seedplan_diagnostic_module.rs`, `HASHES.txt`, `tests-*.log`.

**Limitations.** One opponent, 16 controls, one map diagnosed. No compact/pruning,
no 16-stream equality, no latency, no panel. rustc 1.97.1.

**Next action.** Add a `Return` phase: cancellation must hand the worker back
EMPTY (plant or bank the seed first), and never defer to a `PICK` addressed to a
worker with `free()==0`. Re-run this same 16-control gate before any panel.
