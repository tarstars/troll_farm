---
schema_version: 2
type: handoff
task_id: 20260826-fresh-fixture-dataset
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T144202Z-20260826-fresh-fixture-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 674afb1aca8b69ca7e4e5bebab56a0122cc1a56e
artifact_paths: ["coordination/tasks/20260826-fresh-fixture-dataset.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T14:42:02Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes — new charter, board row 0-3, queued behind T-1's first tables

# handoff: 0-3 — fixtures become a generated dataset cut from real instrumented ladder games of the current bot (owner: "retire old data, build fresh")

Card: `coordination/tasks/20260826-fresh-fixture-dataset.md`. The 34 OSC fixtures are retired as gates (diagnosis: `local_claude_1/fixtures/fixture-drift-2026-08-26.md` — nothing rotted; they were the very-old bot's episodes). Deliverable: `cut_fixtures.py` — given the collector's corpus and a bot hash, cut windows of interest (dances, parked, blocked, stalls, shack engine not starting, `ka` > 30) from that bot's real games with v6 telemetry into a library tagged with bot hash / game / seat / window; regenerate-on-demand; the harness grades from it; a first library from the instrument's first day. **Start after T-1's first two tables and once 0-3a (champion + v6) has been on the ladder a day** — the data does not exist before that. 1–2 days, claude_1 reviews once.
