---
schema_version: 2
type: progress
task_id: 20260731-f1-opponent-archetype-readiness
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260814T062957Z-20260731-f1-opponent-archetype-readiness-progress.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-14T06:29:57Z
---

# Clarification: F1 used sanctioned user-cache scratch, not a replacement bulk root

The exact restore path was
`/home/tarstars/.cache/troll-farm/f1-opponent-archetype-readiness/a2-0b-trajectories-referee-9854000-9854127.ndjson`.
It was a read-only, size-guarded cold-archive retrieval of one pinned 250 MiB input into local
scratch, authorized by the coordinator after the `medium_data` blocker; it did not create or
write through any project bulk root and did not represent the volume as mounted.

Therefore the two host observations agree: `medium_data` remained absent throughout, while the
one frozen F1 source was available from the verified cold archive at the SHA-256 recorded in the
handoff. This restore does **not** make A-5's 17-game or 5,100-decision packages reachable; A-5
must independently locate and authorize its exact inputs or report the storage blocker.

