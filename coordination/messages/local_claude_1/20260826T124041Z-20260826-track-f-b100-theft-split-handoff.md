---
schema_version: 2
type: handoff
task_id: 20260826-track-f-b100-theft-split
from: local_claude_1
to: ["codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T124041Z-20260826-track-f-b100-theft-split-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: bacdee559197c751ca602cc783e02f6af6cf2e9f
artifact_paths: ["coordination/tasks/20260826-track-f-b100-theft-split.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T12:40:41Z
---

- To: codex_1
- CC: user, chatgpt_1, claude_1
- Task: 20260826-track-f-b100-theft-split
- Requires acknowledgement: yes — a new charter, Track F's first read

# handoff: Track F-1 — who ate the b100 banana farm? theft vs own-crop on the Aug-2 ladder games (read-only, 1 day, after T-1's game identification)

Card: `coordination/tasks/20260826-track-f-b100-theft-split.md`. The one ladder trial of a banana
farm (agent `6590083`, submission `41081195`, 2026-08-02) scored 12.99 against the parent's 23.3
while the bench said +79; the bench also showed the opponent +83 and nobody split that into
"ate our bananas" vs "grew their own" (the CBF spec §2 marks it UNRESOLVED). That split decides
whether a conditional farm with an abort is worth building at all. Per-game table, attribution
rule stated and hand-checked on three games, and whether the CBF abort sensor would have fired
and when. Done / dead / budget in the card; gate F-G1 = claude_1, one round.

Sequenced after T-1's game-identification step (same code); no farm design starts before T-1 and
F-1 have answered and the owner has said go. No bot source, no Arena.
