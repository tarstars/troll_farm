---
schema_version: 2
type: update
task_id: 20260826-track-t-f-storage-deferred
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260826T132944Z-20260826-track-t-f-storage-deferred.md
requires_ack: false
ack_for: ["coordination/messages/codex_1/20260826T125200Z-20260826-track-t-top10-field-comparison-ack.md", "coordination/messages/codex_1/20260826T125201Z-20260826-track-f-b100-theft-split-ack.md"]
supersedes: []
created_utc: 2026-08-26T13:29:44Z
---

- To: codex_1 (self)
- CC: local_claude_1, claude_1, user
- Task: 20260826-track-t-f-storage-deferred
- Requires acknowledgement: no — replacement card discharging the two self-addressed queue anchors
- cross-task: `ack_for` names the Track T and Track F acceptance messages because this one card
  preserves their shared storage blocker and strict T-then-F sequencing without duplicating the
  same external-state obligation in two live queue anchors.

# DEFERRED — Track T first, then Track F, when the canonical corpus is readable

This card carries the remaining obligations from the two accepted read-only tracks and discharges
their self-addressed acknowledgement anchors.

1. **Track T-1 first.** Resume `20260826-track-t-top10-field-comparison` only when
   `python3 cgauto/check_external_storage.py --intent read` exits 0 and
   `data/processed/games.jsonl` is readable in this worktree. Produce the shared strong-agent game
   identification and first planting table under `codex_1/top10/`; no build and no Arena action.
2. **Track F-1 second.** Resume `20260826-track-f-b100-theft-split` only after the same storage
   checks pass and Track T has produced its first reproducible game-identification count. Reuse
   that identification under `codex_1/farm/`; no bot-source edit, build, or Arena action.

No corpus content has been opened, no parser has been run, and no unapproved physical path has
been substituted while the approved backend is absent.
