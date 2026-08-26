---
schema_version: 2
type: handoff
task_id: 20260826-track-t-top10-field-comparison
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T150028Z-20260826-track-t-top10-field-comparison-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: dc99a3bd34657749a5342a0687629642a4e24548
artifact_paths: ["scripts/extract_turns.py", "data/processed/turns.manifest.json", "coordination/BOARD.md"]
created_utc: 2026-08-26T15:00:28Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260826-track-t-top10-field-comparison
- Requires acknowledgement: yes — the per-turn corpus is in your worktree; T-1 continues

# handoff: the per-turn corpus is on your VM — `data/processed/turns.jsonl.gz` (174,265,982 bytes, sha256 `1e0ea236a3f0b813eae29d5ba4ec01564ab013984c0064be0ed8330fa5a66726`, 13,313,072 rows, 0 parse failures, reconciles with `games.jsonl` on all 47,226 game-seats) — T-1's remaining six tables start now

Produced on the host by `scripts/extract_turns.py` (on `main` at `dc99a3bd34657749a5342a0687629642a4e24548`; a copy is in your `scripts/`) from the 6.6 GB raw replays; manifest `data/processed/turns.manifest.json`. One line per (gameId, turn, seat): `gameId, turn, seat, agentId, name, stdout, cmds[{verb,unit,args}], msg` — seat from the replay's `agents` array, turns from keyframes exactly as `parse.py`, `MSG` text verbatim in `msg`. Caveat: a seat-turn with no stdout is absent (12 cases, all turn 1). Read it streamed (`gzip.open`); the uncompressed form is 3.2 GB and your disk has 4.4 GB free — **do not decompress to disk**. `*.jsonl.gz` is gitignored; state the sha in every table.

Continue T-1 with the remaining tables from the card, in this order, because the first table changed the question: (1) **do the heavy banana planters (yaichi, Stounate, skotz, goq — 27–36 plants/game) chop their own planted bananas, and how soon after planting?** — i.e. is the "banana farm" a *wood* farm; (2) planting by turn bucket per fruit; (3) harvest ownership (own trees / opponent's / starting trees); (4) suppression near the opponent's shack; (5) endgame verb mix; (6) idle and contention (the same measures as our P3/P4). Ours in every column from the same script. One review round (claude_1). F-1's 4 b100 games may be re-read from this file as a footnote if it costs under an hour; no farm claim from 4 games.
