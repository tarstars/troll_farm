# RESULT — policy-anchored macro rollout controller: built, inert, cause found

**Verdict: PARK the controller as built; the mechanism is unreachable for this
parent, and the reason is measured, not inferred.** `MacroBot` owns the
unchanged parent `SearchBot` (it issues every unit command and is the
deterministic fallback) and adds one predeclared complete economic plan — a
**funded third troll** — priced through the real referee over an equal horizon
against the same parent continuation, under two cheap predeclared opponent
continuations (own-side / contests-our-door), conservative min over both
hypotheses and both checkpoints, MIN_GAIN 1.0. The continuation is an explicit
cheap MODEL of both seats, not a prediction of either real policy.

**Panels (both predeclared variants, frozen before any result).** Variant A
(horizon 24/12) and B (60/30), 192 pairs 9947500..07 x 12 adaptive opponents x
both seats: candidate **167/6/19 = 170.0 vs baseline 167/6/19 = 170.0, delta
+0.0**, own 231.35, opp 116.92, issues 1 vs 1, crit 0/0, 0 score-changed and 0
outcome-changed pairs, all 12 opponents +0.0. 192/192 baseline arrays match gap
210944. The gate (positive W+0.5D) is **not met**: the candidate is bit-identical
to the parent.

**Cause (8 real official streams, 1,997 turns).** The macro window was open with
roster 2 for **1,189 turns**, yet **evaluations 0**: on every one of those turns
the bank was short of PLUM, LEMON and IRON for both bills (`training_cost(2,
spec)`). V439 banks banana/wood and never mines, so a third troll is unaffordable
by construction — searches 0, activations 0, completions 0, rejections 0.

**Files (new family only; parent/bot.rs/submission.rs untouched).**
`claude_candidate_macroplan_core.rs` `e2ff59cc`, `claude_candidate_macroplan.py`
`e3cc05c8`, `test_claude_candidate_macroplan.rs` `288b5fc0`; generated `_a.rs`
`93a801a4`, `_a_module.rs` `1d984d29`, `_a_tests.rs` `c931a61e`,
`_control_module.rs` `526cd9cc` (variant A in `variant_a/`).

**Tests: 9 run, 9 pass** (rustc 1.90.0, `--test-threads=1`): disabled controller
== parent, closed window/empty bank == parent, complete charged transaction,
model legal over the full horizon, endgame/budget closure.

**Prerequisites (all passed).** Compact **94,009 UTF-16**; original==pruned==
compact on 16 archived real streams / 4,312 turns, 0 mismatches; interactive max
**26.8 ms** measured idle.

**Evidence:** `PLAN.md`, `summary-a.txt`, `summary-b.txt`, `panel*.tsv`,
`baseline-verify.txt`, `tests-2.log`/`tests-3.log`, `activation-probe.log`,
`stream-equality.log`, `export.txt`, `hashes.txt`.

**Limitations.** Fixtures are constructed, not real-map states; real-state
evidence is the probe and the panels. The model is crude and was never exercised
on an affordable bill. No commit/platform action; no jobs left running.

**Next action.** Extend the macro plan to a two-stage *acquire-then-train*
commitment (MINE iron plus plum/lemon trips, reusing the dispatch family's tested
funding primitives) — or drop workforce funding and re-aim this same anchored
rollout at a plan the parent's own banana/wood stock can pay for.
