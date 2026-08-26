---
schema_version: 2
type: update
task_id: 20260826-p4b-pipeline-integration
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T132718Z-20260826-p4b-pipeline-integration-deferred.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-26T13:27:18Z
---

- To: codex_1 (self)
- CC: local_claude_1, claude_1, user
- Task: 20260826-p4b-pipeline-integration
- Requires acknowledgement: no — replacement card for work not authorised in the current write set

# DEFERRED — integrate the accepted parked-troll decoder behind the panel API

Candidate 3's independent Gate-1 reproduction is complete. Its parked-troll gate remains
`NOT_EVALUABLE` because `claude_1/pipeline/fuzz_panel.py` imports
`claude_1/pipeline/p4b_gate.py` and calls `evaluate_rows`, while the accepted v4/v5/v6 decoder at
`codex_1/p4b/p4b_gate.py` does not expose that API.

This is not a drop-in copy. The destination belongs to claude_1's private write set, and no current
task transfers it to codex_1. Resume only after the coordinator publishes a task naming the
integration owner, exact destination write set, compatibility contract, and fresh differential
gate. Until then no proxy, v6 parked count, or manual reinterpretation closes P4b.

Candidate 3 itself must not advance regardless: its pre-registered absolute-form risk gate fires
at `ka=171` and the fresh panel reproduces a 65-point own-score loss. No Arena action is pending.
