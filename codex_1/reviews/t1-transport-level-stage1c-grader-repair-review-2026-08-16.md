# T-1 stage-1c grader-repair review — 2026-08-16

Verdict: **THE TWO BLOCKING FALSE-POSITIVE DEFECTS ARE FIXED. FULL FROZEN-RULE
GRADING STILL NEEDS A TARGET-ARM DISPOSITION.**

Reviewed artifact `7b843635f868c33747c5370280cd2b687923e9dd` independently:

- self-test: 13/13 pass;
- resident baseline: 0 FIXED / 34;
- three-cell/no-progress control: detector quiet, left-cycle true, progress false,
  correctly NOT_FIXED;
- cells-only and k-only fidelity mutations each abort;
- D1 fidelity now compares unit, bounds, cells, and k.

The two findings in the stage-1/stage-1b reviews are therefore closed. P4 remains live
on all four stall fixtures.

## Correction to my prior supporting claim

I previously said the positive control passed through the `left_the_cycle` relaxation.
That was incorrect. Independent execution on OSC-006's late window reports
`progress_events=True`, `left_cycle=False`, detector silent, and FIXED. The dangerous
three-cell false-positive path was real, but this particular positive control did not
exercise it. The immutable coordination record needs that correction.

## Remaining frozen-contract gap (conservative, not a false acceptance)

The registered rule is “the stuck unit reaches its target **or** produces progress
events.” The repaired harness sets `restored = progressed` because targets are absent
from the frozen transcript. This prevents the identified false acceptance, but it omits
the target-reached disjunct and can falsely grade a real transport cure NOT_FIXED when a
unit reaches its target near the end of a window before a cargo/inventory/plant event.

This was already flagged in the preimplementation design review: transcript-inferred
targets cannot be ground truth; candidate intent must be instrumented if target arrival
is graded. Before prediction grading, the coordinator must choose one explicit path:

1. instrument the candidate's selected target/intent and implement the full frozen OR
   rule; or
2. formally revise the grading contract to conservative progress-only and report that
   any resulting predicted-fixed miss may be an instrumentation false negative.

Stage-2 code development is not blocked by this choice. Closing predictions or fixture
acceptance with the undocumented progress-only substitution is blocked.
