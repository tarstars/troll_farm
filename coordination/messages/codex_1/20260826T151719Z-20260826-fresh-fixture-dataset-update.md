---
schema_version: 2
type: update
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T151719Z-20260826-fresh-fixture-dataset-update.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260826T151133Z-20260826-fresh-fixture-dataset-ack.md"]
supersedes: []
created_utc: 2026-08-26T15:17:19Z
---

- To: codex_1 (my standing queue)
- CC: local_claude_1, claude_1, user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes — replacement card for time-gated work

DEFERRED: Track 0-3 starts after the first full day of champion version-6 instrument games is collected and the first game's 328-character payload decodes without truncation. Track T's final tables are delivered at `e95efe41`; the corpus and ladder gates are otherwise met.

UNBLOCK-SIGNAL: a pushed coordinator or reviewer message records both (1) at least one full collector day for submission `41198581` and (2) one collected game's version-6 payload decoding without truncation. Then write `cut_fixtures.py` against the hash-pinned corpus as the task card requires.
