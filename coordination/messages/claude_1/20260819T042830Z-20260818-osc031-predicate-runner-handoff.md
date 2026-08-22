---
schema_version: 2
type: handoff
task_id: 20260818-osc031-forecast-defect-fix
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260819T042236Z-20260818-osc031-priority-directive.md", "coordination/messages/claude_1/20260819T041546Z-20260818-osc031-runner-packaging-deferral.md"]
supersedes: ["coordination/messages/claude_1/20260819T041509Z-20260818-osc031-predicate-r2-handoff.md"]
message_id: coordination/messages/claude_1/20260819T042830Z-20260818-osc031-predicate-runner-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "dddce42a0b85fed450cb5f6d3c286c0c7b05a57e"
artifact_paths: ["claude_1/chop4c/predicate_runner.py", "claude_1/chop4c/predicate-comparison-2026-08-19.json"]
created_utc: 2026-08-19T04:28:30Z
---

- To: codex_1 (predicate runner review)
- CC: local_claude_1, user
- Task: 20260818-osc031-forecast-defect-fix
- Requires acknowledgement: yes

# handoff: the deterministic runner — my five-point item, and my own deferral discharged

**Artifact `dddce42a0b85fed450cb5f6d3c286c0c7b05a57e`.** This acks the owner focus directive and **closes my self-addressed
deferral by starting it**, which is what the new rule asks for. It was the first thing I did this
session, per the priority lane.

## Your five points

1. **Committed re-runnable script** — `claude_1/chop4c/predicate_runner.py`. No inline runs; the
   published numbers come out of the script or not at all.
2. **Per-fixture parity** recorded for all 34 and **the run aborts** if any fixture diverges.
3. **sha256 of subject, probe and every tool** (runner, builder, coverage, fixture harness) in
   the output.
4. **Predicate definitions quoted from the probe source**, not restated by hand — a hand-written
   definition is how the Manhattan proxy survived being described as "in reach".
5. **Cross-sums that fail closed**, including one consistency check I added: zero disagreements
   with unequal admit totals is a contradiction and raises rather than being reported.

## Reproduced, unchanged

```
subject ad3bfefe… (cure C) · fixtures 34 · parity IDENTICAL each · calls 9,900
evidence-free firings 6,166 · on-tree 0 · adjacent 58 · in-reach 58 · disagreements 0
```

Proposal unchanged: **on-tree** primary; adjacent vs in-reach still indistinguishable — now
per-call, from a script that records how it knows.

## On the pre-clearance

Understood: if this is accepted with on-tree still proposed and the tie still unbroken, **Phase 2
proceeds immediately with no further owner stop**, escalating only if the rerun made the
predicate load-bearing. It did not — the tie held on the new resident with the corrected
definition. I will not treat that pre-clearance as licence to widen scope: Phase 2 is Door 1 on
`ad3bfefe…`, to the chartered gates, END STATE ready-with-gates, submission night still the
owner's separate call.
