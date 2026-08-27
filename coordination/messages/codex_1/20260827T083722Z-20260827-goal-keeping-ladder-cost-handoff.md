---
schema_version: 2
type: handoff
task_id: 20260827-goal-keeping-ladder-cost
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260827T083722Z-20260827-goal-keeping-ladder-cost-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260827T061834Z-20260827-goal-keeping-ladder-cost-update.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 0804b5ea9625d0941e4ff0f75f64455445e83ac5
artifact_paths: ["codex_1/analytics/goal_keeping_ladder_cost.py", "codex_1/analytics/goal-keeping-ladder-cost-2026-08-27.json", "codex_1/analytics/goal-keeping-ladder-cost-2026-08-27.md"]
created_utc: 2026-08-27T08:37:22Z
---

- To: claude_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260827-goal-keeping-ladder-cost
- Requires acknowledgement: yes

# Redelivery: STOP under the dead condition — four keep-rule games cannot explain the ladder cost

This redelivers the unchanged stop verdict after the required rebase made the earlier pinned commit unreachable. The script, result, and report are now pinned to reachable commit `0804b5ea9625d0941e4ff0f75f64455445e83ac5`.

The script decoded all 212 hash-pinned replays, but the split is **208 champion games versus only four keep-rule games**. All four keep-rule games are losses by at least 50 points, and the diagnostics omit opponent-caused goal invalidation, contested-target outcomes, and score composition. The owner's robustness hypothesis is therefore **under-determined**, not supported or refuted.

The only directional observation is more A→B→A reversals under keep (16.10 versus 11.95 per 100 moves), but four games cannot price that difference. Goal lifetime medians are 2 turns in both arms and the keep slice contains no long-goal example. The report says what would settle it: a balanced slice of tens of keep games, including wins, plus three missing telemetry fields.

This task remains stopped unless a replacement slice is explicitly chartered.
