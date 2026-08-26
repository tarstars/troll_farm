---
schema_version: 2
type: handoff
task_id: 20260822-peek-planner-target-map
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260822T194100Z-20260822-peek-planner-target-map-construction-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: fc332164e73c5734ff3fd6b17368314d95b387b5
artifact_paths: ["codex_1/reviews/peek-planner-target-map-construction-ruling-2026-08-22.md"]
created_utc: 2026-08-22T19:41:00Z
---

- To: claude_1, local_claude_1
- CC: chatgpt_1, user
- Task: 20260822-peek-planner-target-map
- Requires acknowledgement: yes

# HANDOFF — PEEK step-2 construction ACCEPTED, tick-local and fail-closed

The construction is ruled before build. Selection may mechanically propagate the exact chosen
`Candidate.target` in a tick-local `BTreeMap<i32, Target>` borrowed by the resolver during the same
`commands()` call and never stored. Missing/`None` fails toward not displacing; no prior-turn value
can enter the seam.

The swap predicate requires genuine mover pass-through plus a present partner target different from
both the mover's final target and the landing cell being taken. The mover clause is separately
justified and must be measured separately from PEEK. Candidate generation, scoring, ordering,
selection decisions, persistent state, and non-displacement uses remain untouched.

Artifact: `codex_1/reviews/peek-planner-target-map-construction-ruling-2026-08-22.md` at
`agent/codex_1@fc332164e73c5734ff3fd6b17368314d95b387b5`.

DEFERRED: rev-3 build/measurement to the work owner under the task sequence. No source was edited,
no candidate was built, and no Arena action is authorized by this ruling.
