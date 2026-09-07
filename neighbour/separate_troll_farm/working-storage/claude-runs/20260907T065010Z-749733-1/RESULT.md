# RESULT — funding implemented, really activates, never pays; bill infeasible

**Verdict: the missing acquire -> deliver -> pay -> produce commitment is
implemented and it DOES activate on the actual unmodified known map, but no plan
reaches payment, so the hard prerequisite fails and NO 192-pair panel was run.
The family looks structurally infeasible for this parent, and the reason is
measured.**

**Real-map activation (9947500..07, both seats, adaptive opponent 0, 16 pairs,
OFF/ON in one paired runner).** 4 evaluations, 1 activation, 3 rejections. On
9947505 seat 1 the plan opened at turn 60, spec (2,1,1,1), bill
[P6,L3,A3,-,I3,-], bank [0,0,8,4,1,1], ETA 36. By turn 76 it had banked
[6,0,8,4,3,3]: PLUM 0->6 and IRON 1->3 fetched, delivered and banked in 16 turns
through the real referee, then cancelled: the turn-76 census holds no LEMON
tree, so 3 of the bill are unobtainable. 15/16 pairs are bit-identical
to the parent; 16/16 baseline arrays match gap 210944. Competitive: baseline
7/6/3 = 10.0, candidate 8/5/3 = 10.5; own 148->184, opponent 148->180 on the one
diverging pair; issues 0 vs 1 (move_blocked), critical 0 vs 0.

**Feasibility census (same 16 real games, every 10th window turn).** A fruited
PLUM *and* LEMON *and* APPLE tree coexist on only 15/192 = 7.8% of macro-window
turns, and 11/16 games never have such a turn. Every legal spec bills all three
fruits plus IRON, so the third-troll bill is usually unfundable, and the trees
keep being chopped during the tens of turns acquisition needs.

**Changed files** (owned family only; parent/bot.rs/submission.rs untouched):
claude_candidate_macroplan_core.rs 0dce250c, test_claude_candidate_macroplan.rs
779321dc; generated _a.rs 744cf8f9, _a_module.rs 99eb96ff, _a_tests.rs 30d54aef;
unchanged _control_module.rs 526cd9cc and .py e3cc05c8. Prior family archived in
archive-062139/.

**Tests: 13 run, 13 pass** (rustc 1.90.0, --test-threads=1): parent equality
disabled; closed window; empty bank now opens an acquisition (semantics changed
from 062139, justified inline); unfundable bill never opens; acquisition to
payment and a real third worker through the referee, no hp0 HARVEST, seed spent
once; clone isolation and deadline cancellation; model legality; endgame/budget.

**Evidence:** PLAN.md (frozen before editing), activation-final.tsv,
baseline-verify.txt, macro-diagnostic4.log, tree-census-summary.txt, tests-3.log.

**Limitations.** No payment/spawn on a real map, hence no panel, no 16-stream
equality run, no latency measurement. Compact export is 100,016 UTF-16, 16 over
the limit. Probe used opponent index 0 only. All jobs collected.

**Next action.** Park this family on the census, or re-aim the same anchored
controller at a plan the parent's own banana/wood stock can pay for.
