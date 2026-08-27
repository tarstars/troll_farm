---
schema_version: 2
type: handoff
task_id: 20260827-goal-keeping-ladder-cost
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260827T060643Z-20260827-goal-keeping-ladder-cost-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: ada5607900e237db4264ccf9c23d17e54253f368
artifact_paths: ["coordination/tasks/20260827-goal-keeping-ladder-cost.md", "coordination/BOARD.md"]
created_utc: 2026-08-27T06:06:43Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-goal-keeping-ladder-cost
- Requires acknowledgement: yes — a new charter from the owner

# handoff: T-3 — explain why keeping a goal costs ~3 ladder points while costing ~0.27 fruit a game on the bench (the owner's hypothesis: rigidity costs adaptivity, and adaptivity only pays against opponents who contest)

Card: `coordination/tasks/20260827-goal-keeping-ladder-cost.md`. The puzzle in one line: the keep-your-goal rule **reduced** stuck-troll games on the bench (52 → 40) and cost 65 fruit over 240 games, yet its ladder readings are 18.4 and 19.2 against the champion's 21.8, 21.6, 22.1 — about three points, no overlap.

You have what it takes to answer this and nobody has had it before: **both bots' own real ladder games, annotated per turn**. Compare them by one script on goal lifetimes; goals invalidated by the opponent (tree taken, cell occupied, plant gone) and what the troll did next; wasted moves; walking versus working; contested trees won and lost; score composition and its timing; and the same measures split by games won and lost badly. Every number with its game count, and a one-paragraph verdict on the hypothesis — supported, refuted, or under-determined, and what would settle it. One review round (claude_1), one day, no Arena, no builds. Ask for more replay slices whenever the sample is thin; the collector adds ~400 games a night and both bots keep playing.
