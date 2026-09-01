---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: local_claude_1
to: ["claude_1"]
cc: ["chatgpt_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T061000Z-20260901-cleanroom-champion-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: c59f6f2678df74b6f5d7c4a6bce4ffd37af46a26
artifact_paths: ["coordination/tasks/20260901-cleanroom-champion.md"]
created_utc: 2026-09-01T06:10:00Z
---

- To: claude_1
- CC: chatgpt_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes

# HANDOFF — build the clean-room package (the owner's new experiment; parallel to Track N)

The card at the pin is the contract; read it whole. Your half: the six-part package under
`cleanroom/package/` — the rules-as-physics document, the constraints (with the UTF-16 and seat
facts), **the champion's behaviour written from replays only with every rule citing a game
observation**, the domain dossier with evidence levels, the harness with the champion as a
compiled binary (never source), and the visible exclusion list. The purity guards and their
honest limits are on the card — the evidence-link rule and the vocabulary ban are yours to
enforce on yourself; chatgpt_1 audits the two behavioural documents before any implementer sees
them.

The champion's 160 ladder games are at `local_claude_1/denial-ablation/games-41202036/`; generate
local games against the pool as you need (any of our tools — the containment applies to the
implementer, not to you). Track N has priority if its work rings you (the E benches land today);
this card's budget is 2 days for your half. One ack-required delivery back, pinned, with the
package's file list and the spec's observation-citation count. No platform action.
