---
schema_version: 2
type: handoff
task_id: 20260826-champion-instrument-v6
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T144200Z-20260826-champion-instrument-v6-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 674afb1aca8b69ca7e4e5bebab56a0122cc1a56e
artifact_paths: ["coordination/tasks/20260826-champion-instrument-v6.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T14:42:00Z
---

- To: claude_1
- CC: codex_1, user, chatgpt_1
- Task: 20260826-champion-instrument-v6
- Requires acknowledgement: yes — new charter, board row 0-3a; the coordinator submits the result

# handoff: 0-3a — the champion + v6 telemetry, nothing else, for the ladder (owner 1a: "the instrument replaces the champion")

Card: `coordination/tasks/20260826-champion-instrument-v6.md`. The owner's evidence base from now on is **real ladder games of the current bot with telemetry**, so the ladder resident becomes the champion readable `ad1ae4ef` + `narrate6` `MSG` lines and **no rule change**. Gate: probe parity — the arm with `MSG` stripped byte-identical in play to the champion on 240 + 34 (you did exactly this for Candidate 3's instrument); determinism; 0 decode errors; compacted file + sha256 + round-trip report on `main`. codex_1 reviews once; then the coordinator submits it (slot 1). ½ day. Do this **before** D-4 — it is smaller and it starts the data clock.
