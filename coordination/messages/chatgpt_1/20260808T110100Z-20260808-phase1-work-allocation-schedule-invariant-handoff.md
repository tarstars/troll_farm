---
schema_version: 2
type: handoff
task_id: 20260808-phase1-work-allocation
from: chatgpt_1
to: claude_1
cc: ["user", "local_claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260808T110100Z-20260808-phase1-work-allocation-schedule-invariant-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260808T100000Z-20260808-phase1-work-allocation-policy.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: cad16c4decf2eea72a8fc861725d9e3bd50502ad
artifact_paths: ["chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md"]
created_utc: 2026-08-08T11:01:00Z
---

# Handoff: I-30 schedule/opponent-production invariant specification

Item 6 is specified for implementation.

I-30 is a paired, exact accounting invariant that separates:

- opponent deposits originating from our assets (`D_DIRECT`);
- opponent deposits from opponent-created and natural assets (`D_SCHEDULE`);
- score-bearing opponent TRAIN spending (`D_TRAIN`);
- terminal opponent-score delta (`D_OPP`).

With complete provenance, every pair must satisfy exactly:

```text
D_OPP = D_DIRECT + (D_SCHEDULE - D_TRAIN)
```

The indirect term `SCHEDULE_WINDFALL = D_SCHEDULE - D_TRAIN` exposes the D89a-class blind spot
where D-6 remains zero while opponent production expands. Unknown provenance and conservation
residual are raw-zero instrument requirements.

The spec freezes pair identity, event provenance, statuses, JSON outputs and fifteen bite-tests,
including a synthetic case where all existing behavioural invariants and D-6 pass but I-30 sees
additional opponent-own production.

It deliberately does **not** invent a value threshold. An owner-frozen, hash-pinned bound is a
separate required input. An active result without that bound maps to `GATE_UNREADY`, never PASS.

Implementation boundary: measurement ledger, analyzer, fixtures and docs only. No bot, candidate,
parent, host game, value protocol, TestSession, submission, restore or Arena edit. Execution review
belongs to `local_claude_1` under the allocation.
