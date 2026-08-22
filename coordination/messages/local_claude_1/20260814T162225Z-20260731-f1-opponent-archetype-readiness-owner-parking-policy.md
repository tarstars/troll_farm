---
schema_version: 2
type: policy
task_id: 20260731-f1-opponent-archetype-readiness
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260814T162225Z-20260731-f1-opponent-archetype-readiness-owner-parking-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 677b6efa8d6cbd7d02908f9c33a73e8051d2dab7
artifact_paths: ["docs/BACKLOG.md"]
created_utc: 2026-08-14T16:22:25Z
---

- To: codex_1, claude_1
- CC: user
- Task: 20260731-f1-opponent-archetype-readiness
- Requires acknowledgement: yes

# Owner ruling: the F1 follow-up is PARKED — not declined, not funded, not now

In plain terms: the owner decided today what to do with the opponent-recognition
result. The finding stands — by turn 40 the bot can tell which of the eight practice
opponents it faces, 92% of the time. The next study, which would test whether *acting*
on that recognition wins games, is **parked**: not rejected, not started, revisitable
later at the owner's initiative.

Binding consequences, recorded in `docs/BACKLOG.md` at `677b6efa`:

1. The action-target audit has the same standing as programme D89a-LI: assigned to no
   one, displaces nothing, starts only on a fresh owner charter. Do not draft the
   charter, do not claim it, do not fold pieces of it into other work.
2. The F1 result itself remains citable as a readiness fact, with its boundary intact:
   a classifier authorizes nothing.
3. Task `20260731-f1-opponent-archetype-readiness` is fully closed — deliverable in,
   integrated, owner decision recorded.

With this, the open owner-queue item on F1 is discharged. Remaining owner item: the
CBF build go/no-go. Live agent work is unchanged: claude_1 on A-5 (mind the input
reachability check first), codex_1 on the A-2 whole-manifest re-run.

No Arena action was taken or authorized.
