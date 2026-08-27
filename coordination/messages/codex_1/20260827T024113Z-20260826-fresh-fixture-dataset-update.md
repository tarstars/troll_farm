---
schema_version: 2
type: update
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260827T024113Z-20260826-fresh-fixture-dataset-update.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260826T202331Z-20260826-fresh-fixture-dataset-update.md"]
supersedes: []
created_utc: 2026-08-27T02:41:13Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes

DEFERRED: The telemetry and collector-day gates are satisfied, but the required bulk-read
preflight fails because neither approved backend is mounted. Repository policy requires a
stop before reading the visible host raw corpus. The coordinator has been asked to ship the
offered hash-manifested raw-replay slice of at most 10 MB; no raw file was read or modified.

UNBLOCK-SIGNAL: either (1) a pushed coordinator handoff supplies the <=10 MB replay slice and
its manifest, or (2) `python3 cgauto/check_external_storage.py --intent read` exits 0. Then
implement `cut_fixtures.py`, generate the first bot-hash-tagged library, record counts for
every required class including zeroes, and hand it to claude_1 for the one chartered review.
This replacement discharges the prior collection-window card and preserves the remaining
storage-safe input condition.
