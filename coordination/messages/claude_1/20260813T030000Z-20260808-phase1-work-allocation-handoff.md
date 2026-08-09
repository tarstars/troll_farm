---
schema_version: 2
type: handoff
task_id: 20260808-phase1-work-allocation
from: claude_1
to: ["local_claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/claude_1/20260813T030000Z-20260808-phase1-work-allocation-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: d85d060b25483952b23ec694f5c432f04f8d8e8e
artifact_paths: ["claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py", "claude_1/banana-restoration-r2/bitetest-audit/test_run_mutations_completeness.py", "claude_1/banana-restoration-r2/bitetest-audit/branch_ledger.json", "claude_1/banana-restoration-r2/bitetest-audit/render_branch_ledger.py", "claude_1/banana-restoration-r2/bitetest-audit/test_branch_ledger.py", "claude_1/banana-restoration-r2/bitetest-audit/results/branch-ledger.md"]
created_utc: 2026-08-13T03:00:00Z
---

- To: local_claude_1
- CC: user, codex_1
- Task: 20260808-phase1-work-allocation
- Requires acknowledgement: yes

# Bite-test r2: blockers 4 and 5 repaired. 1, 2, 3 and 6 need a ruling I do not own

Two of the six current blockers from `chatgpt_1`'s `20260812T003000Z` are closed by execution. The
other four are detector-semantics questions and you own detector semantics, so I have scoped them
rather than answered them.

## Blocker 4 — an incomplete experiment is no longer a success

`run_mutations.py` ended `return 0 if control_green else 1`. An experiment in which mutants never
patched, never compiled, or produced no probe digest still exited **0** so long as the *unmutated*
control was green. The evidence was already in `totals` — `patch_failed`, `compile_failed`,
`mutants_run` against `manifest_entries` — and nothing consulted it.

Exit status now describes the experiment, in severity order: **1** if the control is not green
(nothing means anything), **2** if incomplete, **0** only when whole. A subset via `--only` stays
legitimate but must now say so with `--partial`, which records `complete: false` and prints that
the totals describe a subset. Results carry a `completeness` block; schema is
`detector-mutation-results/2`.

```text
CONTROL  pre-repair, 1 of 65 mutants                       exit 0
CONTROL  pre-repair, only mutant fails to patch
         (mutants_run=0, patch_failed=1, control green)    exit 0
REPAIRED both cases                                        exit 2
         acknowledged subset (--partial)                   exit 0, complete=false
```

Five tests, and they **fail on the pre-repair runner** — 3 failures, 3 errors — and pass on the
repaired one. A guard that passes against the code it is supposed to catch is not a guard, so I
checked that rather than assuming it.

## Blocker 5 — the 47-branch tallies are derived now

The audit's four headline tallies said *"counted from the table above"*: true when written, silently
false after any edit. The 47 rows are extracted to `branch_ledger.json`; `render_branch_ledger.py`
projects both the table and the counts; `--check` compares the audit's prose to the data **in both
directions** and exits 2 on drift. Eight tests, each demonstrating the guard failing on
really-perturbed data — a flipped row, a dropped row, tampered prose, an off-axis value.

**Your numbers were right.** The three derivable tallies reproduced the hand-written figures
exactly — `11/5/9/22`, `43/4`, `1/6/40`. They were correct; they simply were not derived from
anything.

**One finding beyond the blocker.** The contract-authority tally — *45 `SETTLED`, 2 `CONFLICT`* — is
**not recoverable from any column of that table**. `D-6 (a1)` carries a visible conflict (`SPEC D-6
vs DESIGN F4`); `D-6 (a2)` carries none, in any cell, yet the audit counts it as the second. So one
of four figures claiming to be counted from the table could not have been. I have made it an
explicit per-row field seeded from the audit's own enumeration, which makes it *stated* rather than
*inferred* — but if `D-6 (a2)`'s conflict has a source I have not found, that source belongs in the
row.

## Blockers 1, 2, 3 and 6 — scoped, not answered

These are detector-semantics rulings. You are the detector-semantics owner and `trace_detectors.py`
is yours; me deciding them unilaterally would be the wrong kind of initiative.

1. **`LIVE` does not establish legal-game reachability.** `LIVE` currently means *a mutation changes
   output on generated parsed traces*. The corpus is not referee-produced, so it cannot witness
   reachability. This is a **labelling** repair I can make today — rename to something like
   `PROBE_SENSITIVE` and state the limit wherever `LIVE` is published — but the word appears in
   accepted dispositions, so renaming it is a semantics decision, not a rename.
2. **D-3 probe.** The committed probe implements only next-cell consistency and uses
   `max(speed, 1)`; it does not implement the same-player conflict-resolution label the audit
   describes. Two honest repairs — implement the label, or correct the audit to describe what the
   probe does. Which is right depends on what D-3 is *for*, which is yours.
3. **D-9 `INSTRUMENT_UNSUPPORTED` rows are stale post-c5.** Four rows carry it; the retired proxy
   and the now-supported paired branches must be separated and recalibrated. This needs the c5
   ruling applied to each row, and D-9 is the detector I have already been wrong about once — my
   `74` was records where the tally axis was episodes.
6. **D-5 conformance on the wrong axis.** Definition conformance is expressed on the empirical
   truth-validity axis, which contradicts the report. Mechanically a one-row change; substantively
   it decides what `VALIDATED_BY_DEFINITION` means, and that is exactly the axis whose meaning is
   under dispute.

**Tell me which of these you want me to execute and on what ruling, and I will.** All four are
small once the semantics are fixed; none is safe for me to fix by picking an interpretation.

## Review

Yours under `SINGLE_REVIEWER_DEGRADED`. What I would attack first: whether `--partial` is a real
guard or an escape hatch that will simply always be passed. My answer is that it forces the subset
into the results file and the operator's console, so a partial result can no longer be published as
whole *silently* — but it does not stop anyone publishing one deliberately, and I would not claim
otherwise.
