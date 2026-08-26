---
schema_version: 2
type: handoff
task_id: 20260826-track-t-top10-field-comparison
from: local_claude_1
to: ["codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T124040Z-20260826-track-t-top10-field-comparison-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: bacdee559197c751ca602cc783e02f6af6cf2e9f
artifact_paths: ["coordination/tasks/20260826-track-t-top10-field-comparison.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T12:40:40Z
---

- To: codex_1
- CC: user, chatgpt_1, claude_1
- Task: 20260826-track-t-top10-field-comparison
- Requires acknowledgement: yes — a new charter, Track T on the board

# handoff: Track T-1 — what the 25 strong two-worker Legend bots do that we don't (read-only on the corpus, 2 days, one review round)

The owner adopted a board organisation today (`coordination/BOARD.md`, read its rules first — two
rows per track, done/dead/budget in every card, two review rounds then decide-or-kill, mail for
handoffs and verdicts only). This is Track T's first row, and the owner wants it **first and
fast**: its planting table (question 4) is Track F's go/no-go input.

Card: `coordination/tasks/20260826-track-t-top10-field-comparison.md` — seven questions, one
table each, ours in the same columns from the same script; a ranked list of "tricks" with their
games and an estimated point value; a paragraph for Track F. Corpus: `data/processed/games.jsonl`
(21,496 games, sha256 `a882e527…`), read-only; do not run `parse.py`. Done / dead / budget are in
the card. Gate T-G1 = claude_1, one round, ack-required.

Order: start now, in parallel with your P4b repair (D-2 on the board); the game-identification
step is shared with F-1 (`20260826-track-f-b100-theft-split`, chartered beside this), so write it
once. First deliverable the owner will read: the "who they are" and "planting" tables, even
before the rest.
