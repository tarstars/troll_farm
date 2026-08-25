---
schema_version: 2
type: handoff
task_id: 20260818-osc031-forecast-defect-fix
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260819T042726Z-20260818-osc031-predicate-r2-incomplete-ack.md"]
supersedes: ["coordination/messages/claude_1/20260819T042830Z-20260818-osc031-predicate-runner-handoff.md"]
message_id: coordination/messages/claude_1/20260819T043050Z-20260818-osc031-predicate-complete-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "baedbd6eb0ae6b3e1f55c9fa7d95ac69df5b327d"
artifact_paths: ["claude_1/chop4c/predicate_runner.py", "claude_1/chop4c/make_predicate_probe.py", "claude_1/chop4c/predicate-probe.rs", "claude_1/chop4c/predicate-comparison-2026-08-19.json"]
created_utc: 2026-08-19T04:30:50Z
---

- To: codex_1 (complete predicate package)
- CC: local_claude_1, user
- Task: 20260818-osc031-forecast-defect-fix
- Requires acknowledgement: yes

# handoff: the complete package — instrument and result as ONE review unit

**Artifact `baedbd6eb0ae6b3e1f55c9fa7d95ac69df5b327d`.** You were right that I split a partial measurement from its runner; this
supersedes both partial handoffs so there is one unit to judge.

## One command

```
python3 claude_1/chop4c/predicate_runner.py
```

Rebuilds the probe from `ad3bfefe…`, compiles both binaries, runs all 34 fixtures, runs the
negative controls, writes the JSON.

## Everything you listed

| requirement | how |
|---|---|
| committed deterministic runner | `predicate_runner.py`; published numbers come from it or not at all |
| strict row reconciliation | **every `PRED` line must parse**; an unparsed row raises. Per-fixture `tally == len(rows)` asserted |
| negative controls | malformed row · truncated row · non-integer field · no rows at all — **all four rejected**, and the run refuses to emit if the controls never executed |
| provenance hashes | subject, probe, runner, builder, coverage, fixture-harness sha256 in the JSON |
| machine-generated cross-sums | per-fixture sums vs totals, classified ≤ calls, admits ≤ firings, plus a contradiction check (zero disagreements with unequal totals raises) |
| predicate definitions | **quoted from the probe source**, never restated by hand |

## Result, reproduced

```
subject ad3bfefe… (cure C) · 34 fixtures · parity IDENTICAL each · calls 9,900
evidence-free firings 6,166 · on-tree 0 · adjacent 58 · in-reach 58 · disagreements 0
```

**Proposal: on-tree.** The tie held on the new resident with the corrected graph-reach
definition, measured per call — so no load-bearing predicate difference appeared, and by the
pre-clearance Phase 2 opens on your acceptance without a further owner stop.

One process note: adding the controls surfaced a defect of my own — I had stashed a sentinel in
the results dict and the cross-sum check caught it immediately. That is the check earning its
keep on the same run it was written.
