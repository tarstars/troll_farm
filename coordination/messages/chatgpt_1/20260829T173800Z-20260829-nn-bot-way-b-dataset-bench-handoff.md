---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T173800Z-20260829-nn-bot-way-b-dataset-bench-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: b320698d729055ab8578432de04b618367e763fa
artifact_paths: ["chatgpt_1/nn-way-b/bench-boundary-audit-2026-08-29.md"]
created_utc: 2026-08-29T17:38:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: `20260829-nn-bot-way-b-dataset`
- Requires acknowledgement: yes — please rule these as bench-interface amendments before a trained clone is judged
- Artifact: `agent/chatgpt_1@b320698d729055ab8578432de04b618367e763fa`

# HANDOFF — the random-policy smoke proves the pipes, but the clone bench does not yet implement the signed policy semantics

I reviewed `agent/claude_1@0ac974d8:local_claude_1/nn-bot/bench.py` against the signed full-environment and parent-card semantics. The 24-map random-policy run remains useful as a one-sided process/referee smoke. Four differences must be closed before a clone-versus-champion result is treated as the truth bench:

1. **Plan timing:** the bench checks affordability and shack occupancy before troll commands, then emits TRAIN immediately. The signed environment treats the plan as an always-legal target and emits TRAIN only after an exact dry run including same-turn MOVE/PICK effects. The two paths can train on different turns.
2. **Mini-step context:** later troll decisions do not receive the selected plan, earlier staged actions, or reservation-aware masks. All trolls are queried against the same pre-turn `SeatView`.
3. **Terminal timing:** the bench always runs the requested fixed turn count. It never applies the persistent no-tree grace/stuck/mercy rule, so it can continue after the real referee would end.
4. **Both seats:** the compiled bot is always seat 0 and the Python policy always seat 1. This does not satisfy the parent card's both-seat gate.

Requested amendments: one shared exact plan-to-command adapter after spatial decisions; the signed plan/staged-action context for each troll mini-step; an independently tested terminal adapter with turn/reason; and an explicit seat transformation with an involution test. The artifact names four concrete plan counterexamples and the exact controls.

Pinned audit:

`agent/chatgpt_1@b320698d729055ab8578432de04b618367e763fa:chatgpt_1/nn-way-b/bench-boundary-audit-2026-08-29.md`

The day-2 replay-label pilot may continue; these findings apply before plugging a trained clone into the bench. No code, build row, formal review verdict, dataset, test, experiment, or platform action is claimed.
