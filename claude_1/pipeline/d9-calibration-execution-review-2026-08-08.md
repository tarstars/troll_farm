# Execution review: D-9 calibration handoff (Phase 1 item 1)

- Reviewer: `claude_1` (execution lens, per the 2026-08-08 Phase 1 allocation)
- Under review: `local_claude_1`'s `20260808T090000Z` handoff and
  `data/analysis/live-agent-6553250/d9-calibration-result-2026-08-08.md`
- Method: I ran the panel's own code paths. Nothing edited; no detector, gate, candidate or
  host surface touched.

## Verdict: **conclusion CONFIRMED, stated reason REFUTED, recommendation must change**

The handoff asked me to attack one specific claim — that the paired clauses genuinely ran,
because "if `parent_cmds` were empty or malformed for these games rather than absent, my
conclusion weakens considerably". I tested exactly that, and found a third possibility the
handoff did not consider.

## MEASURED — `parent_cmds` is not empty, and the paired clauses still never ran

Probe: compile both bots via `fuzz_panel.compile_bot`, build the 240 jobs via
`fuzz_panel.build_jobs`, run the parent through `regression_tests.run_binary_custom` for each
job, parse with `td.CommandParser().parse(c_p)`, and inspect.

**60 of 240 games, first 60 jobs:**

| quantity | result |
|---|---|
| games with empty `parent_cmds` | **0** |
| turns parsed per game | **200** (full horizon, every game) |
| parent command bytes per game | 1,047 – 3,283 (real output) |
| **games in which the parent emits any TRAIN** | **0** |

So the handoff's own claim survives its stated attack — `parent_cmds` is well-formed and
non-empty. **But the paired clauses did not fire for a different reason than the handoff
gives.** `detect_d9` guards the entire paired block with `if p_train is not None:`
(`trace_detectors.py:1210`). With no TRAIN anywhere in the parent's stream, `p_train` stays
`None` and **the whole paired block is skipped** — in all 60 games I ran.

## Why this changes the recommendation

The handoff argues: retire the proxy, keep the paired clauses, which are "demonstrably
correct here (zero false positives where zero is the truth)".

**That inference does not hold.** The paired clauses produced zero episodes because their
precondition never occurs, not because they evaluated the games and correctly found no
displacement. They are **unexercised**, in exactly the sense the plan applies to D-2/D-3/D-8.
Zero output from a branch that never executed is not evidence of correctness.

Consequences:

1. **Retiring `banana_before_train` leaves D-9 wholly inert** under this harness — every
   remaining clause is gated behind a condition that never holds. D-9 should therefore join
   the `UNPROVEN` list, making it **five detectors, not four** (D-2, D-3, D-7, D-8, **D-9**).
   Retiring the proxy is still right; describing what remains as validated is not.
2. **The magnitude of the proxy defect is larger than stated, and now has a mechanism.** The
   unpaired loop breaks at `if first_train is not None and t >= first_train`. With no TRAIN
   ever emitted, that break never fires, so "before TRAIN" means **the entire game**. Every
   banana PICK/PLANT in all 200 turns qualifies. The clause is not mildly over-broad — it is
   unbounded, which is why it reaches 196 episodes across 74 games.
3. **A prerequisite for item #4.** Any fixture built to exercise D-9's paired clauses must
   first produce a game in which the parent TRAINs at all. On this map/opponent mix at a
   200-turn horizon, that never happens. Whether TRAIN is reachable at a longer horizon or
   under a different opponent mix is **UNRESOLVED** and needs settling before D-9 can be
   called anything but `UNPROVEN`.

## CONFIRMED from the handoff, independently

- The parent-vs-parent floor blocks **118/240**; D-9 appears in **74 games / 196 episodes**.
- The units distinction (games vs episodes) is used correctly throughout.
- Its refusal to restore a parent-differential exemption is right: that is the round-6 ROOT-A
  gate the owner removed, and the repair must make the detector correct rather than exempt.
- Adding **D-7** to the unexercised list is correct — it has zero episodes across all 240.

## UNRESOLVED — one arithmetic difference to reconcile

The handoff states retiring D-9 takes 118 blocking games to **46** (a 61% reduction). From my
own floor report I count **63** games in which D-9 is the *strictly* sole blocker, which gives
**118 − 63 = 55**, not 46. The gap is likely another units/definition difference — probably
which co-occurring P-tier violations are counted — and it is the same class of ambiguity as
74-vs-196 and 63-vs-68. **I could not reproduce 46 and do not dispute it; I ask for the
definition.** No decision should quote either figure until they agree.

## What I did not verify

I ran 60 of 240 games, not all 240. The TRAIN-absence result was uniform across those 60 and
across every map class and opponent in that prefix, but "0 of 60" is what I measured; "0 of
240" is inferred. My probe is at
`/tmp/.../scratchpad/probe_d9.py` and is trivially re-runnable at full width.
