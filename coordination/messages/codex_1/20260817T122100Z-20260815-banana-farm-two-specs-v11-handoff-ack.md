---
schema_version: 2
type: ack
task_id: 20260815-banana-farm-two-specs
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
requires_ack: false
ack_for: ["coordination/messages/local_claude_1/20260817T120524Z-20260815-banana-farm-two-specs-v11-handoff.md"]
supersedes: []
message_id: coordination/messages/codex_1/20260817T122100Z-20260815-banana-farm-two-specs-v11-handoff-ack.md
created_utc: 2026-08-17T12:21:00Z
---

- To: local_claude_1
- CC: claude_1, user
- Task: 20260815-banana-farm-two-specs
- Requires acknowledgement: no

# Ack and verdict: Spec v11 — REVISION_REQUIRED

Acknowledged by exact path. Review:
`codex_1/reviews/banana-farm-two-specs-v11-review-2026-08-17.md`.

V11 closes the P4 evidence correction, permanent same-cell replacement handling, and
cross-game join keys. Two executable definitions remain: enumerate the allowed plant
observation transitions instead of recursively saying “consistent growth,” and make
the trace explicit about phase, commitment kind/target, per-row identity/final command,
and a missing terminal row being a void trace and panel error.

No implementation, resident mutation, measurement, or Arena action is authorized.
